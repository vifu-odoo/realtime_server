from fastapi import FastAPI, WebSocket

app = FastAPI()

connections = {}

@app.websocket("/ws/{tracking_id}")
async def websocket_endpoint(websocket: WebSocket, tracking_id: str):
    await websocket.accept()

    if tracking_id not in connections:
        connections[tracking_id] = []

    connections[tracking_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # broadcast to all clients
            for conn in connections[tracking_id]:
                await conn.send_text(data)

    except Exception as e:
        print("Disconnected", e)
        connections[tracking_id].remove(websocket)
