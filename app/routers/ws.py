"""WebSocket endpoint – per-incident pub/sub channel."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.broadcast import manager

router = APIRouter()


@router.websocket("/ws/incident/{incident_id}")
async def incident_ws(websocket: WebSocket, incident_id: int):
    await manager.connect(incident_id, websocket)
    try:
        while True:
            # Keep connection alive; client sends pings as needed
            data = await websocket.receive_text()
            # Echo pings back
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(incident_id, websocket)


@router.websocket("/ws/global")
async def global_ws(websocket: WebSocket):
    """Global channel – receives new-incident notifications."""
    await manager.connect(0, websocket)  # 0 = global channel
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(0, websocket)
