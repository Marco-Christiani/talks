# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "flask",
#     "requests",
#     "flask-cors"
# ]
# ///
# docker_session_server.py
from __future__ import annotations

import itertools
import json
import os
import subprocess
import traceback
import uuid
from dataclasses import asdict, dataclass
from typing import ClassVar, Dict

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # HACK: allow everything

BASE_IMAGE = "dind-runner"


def generate_session_id() -> str:
    uid = uuid.uuid4().hex[:8]
    return f"session-{uid}"


def generate_session_port(sess_id: str) -> int:
    """Crude deterministic mapping from session ID to host port."""
    return 10000 + int(sess_id[-4:], 16) % 5000


@dataclass
class Session:
    id: str  # container name (also session ID)
    port: int  # host port mapped to container's 8000

    @staticmethod
    def from_id(sess_id: str) -> Session:
        port = generate_session_port(sess_id=sess_id)
        return Session(id=sess_id, port=port)


class State:
    _instance: ClassVar[State | None] = None
    _sessions: ClassVar[Dict[str, Session]] = {}

    def __new__(cls, *args, **kwargs) -> State:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls.refresh()
        return cls._instance

    def get_session(self, sess_id: str) -> Session | None:
        return self._sessions.get(sess_id)

    def create_session(self) -> Session:
        sess_id = generate_session_id()
        while sess_id in self._sessions:
            sess_id = generate_session_id()

        sess = Session.from_id(sess_id)
        self._sessions[sess.id] = sess
        return sess

    @classmethod
    def refresh(cls) -> None:
        ls_cmd = ["docker", "container", "ls", "--format", "{{.Names}}", "--filter", f"ancestor={BASE_IMAGE}"]
        proc = subprocess.run(ls_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        results = {}
        for line in proc.stdout.splitlines():
            parts = line.split()
            assert len(parts) == 1
            container_name = parts[0]
            if not container_name.startswith("session-"):
                continue
            inspect_cmd = ["docker", "inspect", "--format", "{{json .NetworkSettings.Ports}}", container_name]
            proc2 = subprocess.run(inspect_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            ports: dict = json.loads(proc2.stdout)

            for binding in ports.values():
                if binding:
                    host_port = int(binding[0]["HostPort"])
                    results[container_name] = Session(id=container_name, port=host_port)
                    break

        for container_name, session in itertools.chain(results.items(), cls._sessions.copy().items()):
            if container_name not in cls._sessions:
                assert container_name == session.id
                print("Found session:", session)
                cls._sessions[container_name] = session
            elif container_name not in results:
                print("Session gone:", session)
                del cls._sessions[container_name]


@app.route("/session", methods=["GET"])
def get_session():
    sess_id = request.args.get("sess")
    wait = bool(request.args.get("wait", False))
    timeout = int(request.args.get("timeout", 3))
    if not sess_id:
        return "Must provide a value for `sess` parameter", 400

    session = State().get_session(sess_id)
    if not session:
        return "Session not found", 404

    if wait and not wait_for_session_instance(session, timeout=timeout):
        return "Session not available", 503

    return "OK", 200


@app.route("/session", methods=["POST"])
def create_session():
    session = State().create_session()
    wait = bool(request.args.get("wait", False))
    timeout = int(request.args.get("timeout", 30))
    try:
        cmd = [
            "docker",
            "run",
            "--privileged",
            "-d",
            "--name",
            session.id,
            "-p",
            f"{session.port}:8000",
            BASE_IMAGE,
        ]
        subprocess.run(cmd, check=True)

        if wait and not wait_for_session_instance(session, timeout):
            _docker_rm(session.id)
            return (f"Session {session.id} failed to become healthy within timeout={timeout}", 503)

        return jsonify(asdict(session))
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/session", methods=["DELETE"])
def delete_session():
    sess_id = request.args.get("sess") or ""
    session = State().get_session(sess_id)
    if session is None:
        return (f"No such session {sess_id}", 422)

    _docker_rm(session.id)
    return ("OK", 200)


@app.route("/run", methods=["POST"])
def proxy_run():
    sess_id = request.args.get("sess") or ""
    session = State().get_session(sess_id)
    if session is None:
        return (f"No such session {sess_id}", 422)

    if not wait_for_session_instance(session, 30):
        return ("Runner not ready", 503)

    try:
        r = requests.post(
            f"http://127.0.0.1:{session.port}/run",
            data=request.data,
            headers={"Content-Type": "application/json"},
        )
        return (r.text, r.status_code)
    except Exception:
        traceback.print_exc()
        return ("Internal error", 500)


def _docker_rm(name: str) -> None:
    subprocess.run(["docker", "rm", "-f", name], check=False)


def wait_for_session_instance(session: Session, timeout: int) -> bool:
    import time

    start = time.time()
    while (time.time() - start) < timeout:
        cmd = ["docker", "inspect", "-f", "{{.State.Health.Status}}", session.id]
        print(" ".join(cmd))
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        status = (proc.stdout or "").strip().lower()
        if status == "healthy":
            return True
        time.sleep(1)

    return False


if __name__ == "__main__":
    State().refresh()
    app.run(port=5000, debug=bool(os.environ.get("DEBUG", False)))
