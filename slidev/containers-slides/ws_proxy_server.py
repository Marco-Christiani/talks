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

# FASTAPI WS PROXY + SESSION BACKEND (replaces Flask backend)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, asyncio, json
import websockets
import docker

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_IMAGE = "dind-runner"
NETWORK_NAME = "containers-slides_workshop"  # compose network name
SESSIONS = {}  # session_id -> container_name

# Initialize Docker client
docker_client = docker.from_env()


class SessionInfo(BaseModel):
    id: str


@app.post("/session")
async def create_session():
    sess_id = f"session-{uuid.uuid4().hex[:8]}"

    try:
        # Find the workshop network (handles compose prefixes dynamically)
        all_networks = docker_client.networks.list()
        workshop_network = None
        for net in all_networks:
            if net.name.endswith("_workshop") or net.name == "workshop":
                workshop_network = net
                break

        if not workshop_network:
            raise Exception(f"No workshop network found. Available networks: {[n.name for n in all_networks]}")

        network_name = workshop_network.name

        # Create container in the same network as the proxy
        container = docker_client.containers.run(
            BASE_IMAGE,
            name=sess_id,
            privileged=True,
            detach=True,
            network=network_name,
            remove=False,  # Don't auto-remove so we can manage lifecycle
        )

        SESSIONS[sess_id] = sess_id
        print(f"Created session {sess_id} in network {network_name}")
        return {"id": sess_id}

    except Exception as e:
        print(f"Error creating session: {e}")
        raise Exception(f"Failed to create session: {e}")


@app.get("/session")
async def get_session(sess: str):
    try:
        container = docker_client.containers.get(sess)
        return {"ok": True, "status": container.status}
    except docker.errors.NotFound:
        return {"ok": False, "error": "Session not found"}


@app.delete("/session")
async def delete_session(sess: str):
    if sess in SESSIONS:
        try:
            container = docker_client.containers.get(sess)
            container.remove(force=True)
            del SESSIONS[sess]
            return {"deleted": sess}
        except docker.errors.NotFound:
            del SESSIONS[sess]
            return {"deleted": sess, "note": "Container already gone"}
        except Exception as e:
            return {"error": f"Failed to delete: {e}"}
    return {"error": "Session not found"}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


@app.websocket("/ws")
async def proxy_ws(client_ws: WebSocket):
    print("WebSocket request received.")
    await client_ws.accept()
    print("WebSocket accepted.")

    sess_id = client_ws.query_params.get("sess")
    print(f"Session ID: {sess_id}")
    print(f"Sessions available: {list(SESSIONS.keys())}")

    if not sess_id or sess_id not in SESSIONS:
        print(f"Session {sess_id} not found in SESSIONS")
        try:
            await client_ws.close(code=1008)
        except:
            pass
        return

    print("Session validation passed")
    container_ws = None
    try:
        print("About to wait for container ready")
        # Wait for container to be ready before connecting
        await wait_for_container_ready(sess_id)
        print("Container is ready")

        # Connect using container name as hostname (Docker networking)
        uri = f"ws://{sess_id}:8000/terminal"
        print(f"Connecting to {uri}")

        container_ws = await websockets.connect(uri)
        print("Connected to container WebSocket")

        async def forward_client_to_container():
            print("Starting client_to_container forwarder")
            try:
                while True:
                    try:
                        message = await client_ws.receive_text()
                        print(f"Received from client: {repr(message)}")

                        # Forward the complete JSON message to maintain protocol compatibility
                        # The Go backend expects the full JSON structure
                        if container_ws:
                            await container_ws.send(message)
                            print(f"Sent to container: {repr(message)}")
                        else:
                            print("Container WS is None, breaking")
                            break
                    except WebSocketDisconnect:
                        print("Client WebSocket disconnected")
                        break
                    except Exception as e:
                        print(f"Error in client_to_container: {e}")
                        break
            except Exception as e:
                print(f"Fatal error in client_to_container: {e}")

        async def forward_container_to_client():
            print("Starting container_to_client forwarder")
            try:
                async for message in container_ws:
                    print(f"Received from container: {repr(message[:100])}")
                    try:
                        await client_ws.send_text(message)
                    except Exception as e:
                        print(f"Failed to send to client: {e}")
                        break
            except Exception as e:
                print(f"Error in container_to_client: {e}")

        # Start both forwarders
        print("Creating tasks")
        task1 = asyncio.create_task(forward_client_to_container())
        task2 = asyncio.create_task(forward_container_to_client())

        print("Started both forwarding tasks")

        # Wait for either task to complete
        done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        print("WebSocket proxy session ended")

    except Exception as e:
        print(f"WebSocket proxy error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Cleaning up")
        # Clean up connections
        if container_ws:
            try:
                await container_ws.close()
            except:
                pass

        try:
            if client_ws.client_state.name != "DISCONNECTED":
                await client_ws.close()
        except:
            pass
        print("Cleanup complete")


async def wait_for_container_ready(sess_id: str, timeout: int = 30):
    """Wait for container to be ready to accept connections"""
    import time

    start_time = time.time()

    while (time.time() - start_time) < timeout:
        try:
            container = docker_client.containers.get(sess_id)
            if container.status == "running":
                # Give the container a moment to fully start services
                await asyncio.sleep(2)

                # Try a quick connection test
                try:
                    test_ws = await asyncio.wait_for(websockets.connect(f"ws://{sess_id}:8000/terminal"), timeout=3.0)
                    await test_ws.close()
                    print(f"Container {sess_id} is ready")
                    return
                except Exception as e:
                    print(f"Container not ready yet: {e}")

            await asyncio.sleep(1)
        except docker.errors.NotFound:
            raise Exception(f"Container {sess_id} not found")

    raise Exception(f"Container {sess_id} not ready after {timeout}s")
