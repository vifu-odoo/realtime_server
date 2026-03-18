from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

app = FastAPI()

# Allow all origins (adjust later for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections per tracking_id
connections: Dict[str, List[WebSocket]] = {}


async def connect(websocket: WebSocket, tracking_id: str):
    await websocket.accept()
    connections.setdefault(tracking_id, []).append(websocket)
    print(f"Connected: {tracking_id} | Total: {len(connections[tracking_id])}")


def disconnect(websocket: WebSocket, tracking_id: str):
    if tracking_id in connections:
        if websocket in connections[tracking_id]:
            connections[tracking_id].remove(websocket)

        if not connections[tracking_id]:
            del connections[tracking_id]

    print(f"Disconnected: {tracking_id}")


async def broadcast(tracking_id: str, message: str):
    if tracking_id not in connections:
        return

    dead_connections = []

    for conn in connections[tracking_id]:
        try:
            await conn.send_text(message)
        except Exception:
            dead_connections.append(conn)

    # Cleanup dead sockets
    for conn in dead_connections:
        disconnect(conn, tracking_id)


@app.websocket("/ws/{tracking_id}")
async def websocket_endpoint(websocket: WebSocket, tracking_id: str):
    await connect(websocket, tracking_id)

    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(tracking_id, data)

    except WebSocketDisconnect:
        disconnect(websocket, tracking_id)

    except Exception as e:
        print("Error:", e)
        disconnect(websocket, tracking_id)