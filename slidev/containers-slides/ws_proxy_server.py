# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "pydantic",
#     "uvicorn",
#     "websockets",
#     "docker",
# ]
# ///

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Dict, Optional

import docker
import docker.errors
import websockets
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import contextlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

app = FastAPI(title="Docker Workshop Proxy", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_IMAGE = "dind-runner"
SESSIONS: Dict[str, str] = {}  # session_id -> container_name

try:
    docker_client = docker.from_env()
    logger.info("Docker client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Docker client: {e}")
    raise


class SessionInfo(BaseModel):
    id: str


class CommandRequest(BaseModel):
    cmd: str
    timeout: Optional[int] = 30


class CommandResponse(BaseModel):
    output: str
    exit_code: int
    error: Optional[str] = None


@app.post("/session", response_model=SessionInfo)
async def create_session():
    """Create a new Docker container session"""
    sess_id = f"session-{uuid.uuid4().hex[:8]}"

    try:
        # Find the workshop network
        all_networks = docker_client.networks.list()
        workshop_network = None
        for net in all_networks:
            if net.name.endswith("_workshop") or net.name == "workshop":
                workshop_network = net
                break

        if not workshop_network:
            available = [n.name for n in all_networks]
            logger.error(f"No workshop network found. Available: {available}")
            raise HTTPException(status_code=500, detail=f"Workshop network not found. Available: {available}")

        network_name = workshop_network.name
        logger.info(f"Using network: {network_name}")

        container = docker_client.containers.run(
            BASE_IMAGE,
            name=sess_id,
            privileged=True,
            detach=True,
            network=network_name,
            remove=False,
            environment={"TERM": "xterm-256color", "DEBIAN_FRONTEND": "noninteractive"},
        )

        SESSIONS[sess_id] = sess_id
        logger.info(f"Created session {sess_id} in network {network_name}")
        return SessionInfo(id=sess_id)

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")


@app.get("/session")
async def get_session(sess: str):
    """Get session status"""
    try:
        container = docker_client.containers.get(sess)
        return {"ok": True, "status": container.status}
    except docker.errors.NotFound:
        return {"ok": False, "error": "Session not found"}


@app.delete("/session")
async def delete_session(sess: str):
    """Delete a session and its container"""
    if sess in SESSIONS:
        try:
            container = docker_client.containers.get(sess)
            container.remove(force=True)
            del SESSIONS[sess]
            logger.info(f"Deleted session {sess}")
            return {"deleted": sess}
        except docker.errors.NotFound:
            del SESSIONS[sess]
            return {"deleted": sess, "note": "Container already gone"}
        except Exception as e:
            logger.error(f"Error deleting session {sess}: {e}")
            return {"error": f"Failed to delete: {e}"}
    return {"error": "Session not found"}


@app.post("/run", response_model=CommandResponse)
async def run_command(sess: str, request: CommandRequest):
    """Execute a command in a session container using docker exec"""
    if sess not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        container = docker_client.containers.get(sess)

        # Execute command in container
        result = container.exec_run(
            request.cmd,
            stderr=True,
            stdout=True,
            tty=False,
            user="root",
        )

        output = result.output.decode("utf-8", errors="replace")

        return CommandResponse(
            output=output,
            exit_code=result.exit_code,
            error=None if result.exit_code == 0 else f"Command exited with code {result.exit_code}",
        )

    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        logger.error(f"Docker API error executing command in {sess}: {e}")
        raise HTTPException(status_code=500, detail=f"Docker error: {e}")
    except Exception as e:
        logger.error(f"Error executing command in session {sess}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        docker_client.ping()
        return {
            "status": "healthy",
            "docker": "connected",
            "active_sessions": len(SESSIONS),
            "sessions": list(SESSIONS.keys()),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "active_sessions": len(SESSIONS)}


@app.websocket("/ws")
async def proxy_ws(client_ws: WebSocket):
    """WebSocket proxy for terminal sessions"""
    logger.info("WebSocket connection initiated")
    await client_ws.accept()

    sess_id = client_ws.query_params.get("sess")

    if not sess_id or sess_id not in SESSIONS:
        logger.warning(f"Invalid session {sess_id}. Available: {list(SESSIONS.keys())}")
        await client_ws.close(code=1008, reason="Session not found")
        return

    logger.info(f"WebSocket proxy starting for session {sess_id}")
    container_ws = None

    try:
        # Wait for container's service to be up
        await wait_for_container_ready(sess_id)

        # Connect to WS
        uri = f"ws://{sess_id}:8000/terminal"
        container_ws = await websockets.connect(uri)
        logger.info(f"Connected to container WebSocket: {uri}")

        async def forward_client_to_container():
            """Forward messages from client to container"""
            try:
                while True:
                    # Forward (JSON) message
                    message = await client_ws.receive_text()
                    await container_ws.send(message)
            except WebSocketDisconnect:
                logger.info("Client disconnected")
            except Exception as e:
                logger.error(f"Client->Container forwarding error: {e}")

        async def forward_container_to_client():
            """Forward messages from container to client"""
            try:
                async for message in container_ws:
                    await client_ws.send_text(message)
            except Exception as e:
                logger.error(f"Container->Client forwarding error: {e}")

        # Start bidirectional forwarding
        client_task = asyncio.create_task(forward_client_to_container())
        container_task = asyncio.create_task(forward_container_to_client())

        # Wait for either connection to close
        done, pending = await asyncio.wait([client_task, container_task], return_when=asyncio.FIRST_COMPLETED)

        # Clean up
        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        logger.info(f"WebSocket session {sess_id} ended")

    except Exception as e:
        logger.error(f"WebSocket proxy error for {sess_id}: {e}")
        with contextlib.suppress(Exception):
            await client_ws.send_text(json.dumps({"type": "error", "data": f"Connection error: {e}"}))
    finally:
        # Cleanup
        if container_ws:
            with contextlib.suppress(Exception):
                await container_ws.close()

        try:
            if client_ws.client_state.name != "DISCONNECTED":
                await client_ws.close()
        except:
            pass

        logger.info(f"Cleaned up WebSocket session {sess_id}")


async def wait_for_container_ready(sess_id: str, timeout: int = 30) -> None:
    """Wait for container to be ready using Docker health check"""
    import time

    start_time = time.time()
    logger.info(f"Waiting for container {sess_id} to be healthy...")

    while (time.time() - start_time) < timeout:
        try:
            container = docker_client.containers.get(sess_id)

            # Check if container has health check configured (it definitely should...)
            if container.attrs.get("Config", {}).get("Healthcheck"):
                # Use Docker health check status
                health_status = container.attrs.get("State", {}).get("Health", {}).get("Status", "").lower()
                logger.debug(f"Container {sess_id} health status: {health_status}")

                if health_status == "healthy":
                    logger.info(f"Container {sess_id} is healthy")
                    return
            else:
                # Fallback: container is running and basic connectivity test
                if container.status == "running":
                    try:
                        result = container.exec_run("echo ready")
                        if result.exit_code == 0:
                            logger.info(f"Container {sess_id} is running and responsive")
                            return
                    except Exception as e:
                        logger.debug(f"Container {sess_id} not responsive yet: {e}")

            await asyncio.sleep(1)

        except docker.errors.NotFound:
            raise Exception(f"Container {sess_id} not found")
        except Exception as e:
            logger.debug(f"Error checking container {sess_id}: {e}")
            await asyncio.sleep(1)

    try:
        container = docker_client.containers.get(sess_id)
        logs = container.logs(tail=10).decode("utf-8", errors="replace")
        logger.error(f"Container {sess_id} failed to become ready. Recent logs:\n{logs}")
    except:
        pass

    raise Exception(f"Container {sess_id} not ready after {timeout}s")


@app.on_event("startup")
async def startup_event():
    logger.info("Docker Workshop Proxy starting up")
    logger.info(f"Base image: {BASE_IMAGE}")
    logger.info(f"Active sessions will be tracked in memory")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down - cleaning up sessions")
    for sess_id in list(SESSIONS.keys()):
        try:
            container = docker_client.containers.get(sess_id)
            container.remove(force=True)
            logger.info(f"Cleaned up session {sess_id}")
        except:
            pass
    SESSIONS.clear()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ws_proxy_server:app", host="0.0.0.0", port=5000, log_level="info", access_log=True)
