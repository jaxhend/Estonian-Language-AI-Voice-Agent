from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
import uuid
import json

from app.bus import bus
from app.schemas.events import ClientAudio, TTSAudio, ManagerAnswer
from app.core.ids import new_id

router = APIRouter()

# A simple dictionary to keep track of active WebSocket connections
active_connections: dict[uuid.UUID, WebSocket] = {}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: uuid.UUID):
    await websocket.accept()
    active_connections[client_id] = websocket
    print(f"Client {client_id} connected. Total clients: {len(active_connections)}")
    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            # In the new client, we only receive JSON strings or audio bytes
            # replace this block inside websocket_endpoint()
            message = await websocket.receive()

            if "text" in message and message["text"] is not None:
                try:
                    data = json.loads(message["text"])
                    text_to_speak = data.get("text")
                    if text_to_speak:
                        answer_event = ManagerAnswer(
                            text=text_to_speak,
                            trace_id=new_id("trace"),
                            client_id=client_id
                        )
                        await bus.publish("manager.answer", answer_event)
                except json.JSONDecodeError:
                    print(f"Received invalid JSON: {message['text']}")

            elif "bytes" in message and message["bytes"] is not None:
                audio_event = ClientAudio(chunk=message["bytes"], client_id=client_id)
                await bus.publish("client.audio", audio_event)

    except WebSocketDisconnect:
        if client_id in active_connections:
            del active_connections[client_id]
        print(f"Client {client_id} disconnected. Total clients: {len(active_connections)}")

@bus.subscribe("tts.audio")
async def on_tts_audio(event: TTSAudio):
    """
    Receives a TTS audio event and sends the audio chunk to the
    correct client's WebSocket.
    """
    if event.client_id in active_connections:
        websocket = active_connections[event.client_id]
        await websocket.send_bytes(event.chunk)
    else:
        print(f"Warning: Received TTS audio for disconnected client {event.client_id}")

