import os
from dotenv import load_dotenv
import uuid, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.bus import bus
from app.schemas.events import ClientAudio, TTSAudio, ManagerAnswer, STTPartial, STTFinal
from app.core.ids import new_id
from app.stt.google_stt import GoogleSTT

router = APIRouter()
active_connections: dict[uuid.UUID, WebSocket] = {}
stt_instances: dict[uuid.UUID, GoogleSTT] = {}

load_dotenv()

print("📋 Registering WebSocket event handlers...")

@bus.subscribe("stt.partial")
@bus.subscribe("stt.final")
async def on_stt_result(event: STTPartial | STTFinal):
    """
    Receives an STT result event and sends it to the correct client's WebSocket.
    """
    print(f"📨 Received STT event: {event.text} (final={event.is_final})")
    if event.client_id in active_connections:
        websocket = active_connections[event.client_id]
        try:
            # Convert to dict and ensure UUID is serialized to string
            data = event.model_dump()
            data['client_id'] = str(data['client_id'])
            if event.is_final:
                data["role"] = "user"
            await websocket.send_json(data)
            print(f"✅ Sent STT result to client {event.client_id}")
        except Exception as e:
            print(f"❌ Error sending STT result to client {event.client_id}: {e}")
    else:
        print(f"⚠️ Client {event.client_id} not in active connections")

@bus.subscribe("tts.audio")
async def on_tts_audio(event: TTSAudio):
    """
    Receives a TTS audio event and sends the audio chunk to the
    correct client's WebSocket.
    """
    if event.client_id in active_connections:
        websocket = active_connections[event.client_id]
        try:
            await websocket.send_bytes(event.chunk)
            # Only log first few chunks to avoid spam
            import random
            if random.random() < 0.1:  # Log ~10% of chunks
                print(f"🔊 Sent {len(event.chunk)} bytes of audio to client {event.client_id}")
        except Exception as e:
            print(f"❌ Error sending audio to client {event.client_id}: {e}")
    else:
        print(f"Warning: Received TTS audio for disconnected client {event.client_id}")

print(f"✅ WebSocket event handlers registered. STT subscribers: {len(bus.subscribers.get('stt.final', []))}")

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: uuid.UUID):
    await websocket.accept()
    active_connections[client_id] = websocket
    print(f"🔌 Client {client_id} connected. Total clients: {len(active_connections)}")

    recognizer_path = (
        f"projects/{os.getenv('PROJECT_ID')}"
        f"/locations/{os.getenv('LOCATION')}"
        f"/recognizers/{os.getenv('RECOGNIZER_NAME')}"
    )
    print(f"🎤 Creating STT instance with recognizer: {recognizer_path}")
    stt = GoogleSTT(client_id=client_id, recognizer_path=recognizer_path, language="en-US")
    stt_instances[client_id] = stt
    await stt.start()

    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            msg = await websocket.receive()

            # text frames
            if (t := msg.get("text")) is not None:
                try:
                    data = json.loads(t)
                except json.JSONDecodeError:
                    # ignore non-JSON text packets
                    continue

                if data.get("type") == "stt_init":
                    await bus.publish(
                        "client.stt_init",
                        type("Init", (), {
                            "client_id": client_id,
                            "sample_rate": data.get("sampleRate", 16000),
                            "encoding": data.get("encoding", "LINEAR16"),
                        })()
                    )
                elif "text" in data and data["text"]:
                    await bus.publish(
                        "manager.answer",
                        ManagerAnswer(text=data["text"], trace_id=new_id("trace"), client_id=client_id)
                    )

            # binary frames (audio)
            elif (b := msg.get("bytes")) is not None:
                print(f"🎵 Received audio chunk: {len(b)} bytes from client {client_id}")
                await bus.publish("client.audio", ClientAudio(chunk=b, client_id=client_id))

    except WebSocketDisconnect:
        print(f"🔌 Client {client_id} disconnected (WebSocketDisconnect)")
        pass
    except Exception as e:
        print(f"❌ Error in WebSocket handler for client {client_id}: {e}")
    finally:
        active_connections.pop(client_id, None)
        stt_inst = stt_instances.pop(client_id, None)
        if stt_inst:
            await stt_inst.stop()
        print(f"🔌 Client {client_id} cleaned up. Remaining clients: {len(active_connections)}")

