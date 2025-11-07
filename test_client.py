import asyncio
import websockets
import pyaudio
import queue

import uuid

# --- Configuration ---
CLIENT_ID = uuid.uuid4()
WEBSOCKET_URI = f"ws://127.0.0.1:8000/ws/{CLIENT_ID}"
CHUNK_SIZE = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# ---

# A queue to hold audio data from the recording callback
audio_queue = queue.Queue()

def audio_callback(in_data, frame_count, time_info, status):
    """This function is called by PyAudio for each new chunk of audio."""
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

async def sender_task(websocket):
    """Takes audio from the queue and sends it over the WebSocket."""
    print("Sender: Started and waiting for audio from microphone...")
    while True:
        try:
            # Get audio data from the queue
            data = await asyncio.get_event_loop().run_in_executor(None, audio_queue.get)
            print(f"Sender: Sending {len(data)} bytes to server.")
            await websocket.send(data)
        except websockets.exceptions.ConnectionClosed:
            print("Sender: Connection closed.")
            break
        except Exception as e:
            print(f"Sender error: {e}")
            break

async def listener_task(websocket, output_stream):
    """Listens for incoming audio data and plays it."""
    print("Listener: Started and waiting for audio from server...")
    while True:
        try:
            audio_data = await websocket.recv()
            print(f"Listener: Received {len(audio_data)} bytes from server. Playing...")
            if isinstance(audio_data, bytes):
                output_stream.write(audio_data)
        except websockets.exceptions.ConnectionClosed:
            print("Listener: Connection closed.")
            break
        except Exception as e:
            print(f"Listener error: {e}")
            break

async def main():
    p = pyaudio.PyAudio()

    try:
        # Open stream for playing back echoed audio
        output_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

        # Open microphone stream using a non-blocking callback
        input_stream = p.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              frames_per_buffer=CHUNK_SIZE,
                              stream_callback=audio_callback)

    except IOError as e:
        print(f"PyAudio Error: {e}")
        p.terminate()
        return

    print("\n🎙️  Microphone is open. Connecting to server...")
    input_stream.start_stream()

    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print(f"✅ Successfully connected to WebSocket server at {WEBSOCKET_URI}")
            print("🔴 Recording... You should hear your own voice echoed back.")
            print("   Press Ctrl+C to stop.")

            # Run sender and listener tasks concurrently
            await asyncio.gather(
                sender_task(websocket),
                listener_task(websocket, output_stream)
            )

    except KeyboardInterrupt:
        print("\n🛑 Recording stopped by user.")
    except ConnectionRefusedError:
        print("\n---")
        print("Error: Connection refused. Please ensure the server is running.")
        print("---\n")
    finally:
        print("Cleaning up resources...")
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()
        print("Done.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

