import asyncio
import websockets
import uuid
import json
import aioconsole
import io
import os
import subprocess

# --- Configuration ---
CLIENT_ID = uuid.uuid4()
WEBSOCKET_URI = f"ws://127.0.0.1:8000/ws/{CLIENT_ID}"
TEMP_AUDIO_FILENAME = "temp_tts_output.mp3"
# ---

async def listen_for_audio(websocket):
    """Listens for incoming audio data, saves it to a file, and plays it."""
    print("🎧 Audio listener started. Waiting for audio from server...")
    mp3_buffer = io.BytesIO()

    try:
        while True:
            message_data = await websocket.recv()

            if isinstance(message_data, bytes):
                # Accumulate MP3 data in the buffer
                mp3_buffer.write(message_data)

            elif isinstance(message_data, str):
                message = json.loads(message_data)
                # Check for the end-of-stream signal from the server
                if message.get("isFinal"):
                    print("End of audio stream signal received.")

                    if mp3_buffer.getbuffer().nbytes > 0:
                        print("Saving and playing audio...")
                        try:
                            # 1. Write the in-memory buffer to a temporary file
                            with open(TEMP_AUDIO_FILENAME, "wb") as f:
                                f.write(mp3_buffer.getvalue())

                            # 2. Use mpg123 to play the audio file
                            # The '-q' flag makes it "quiet" (less console output)
                            subprocess.run(["mpg123", "-q", TEMP_AUDIO_FILENAME])

                            print("Playback finished.")
                        except FileNotFoundError:
                            print("\n---")
                            print("ERROR: 'mpg123' command not found.")
                            print("Please ensure you have installed it with: brew install mpg123")
                            print("---\n")
                        except Exception as e:
                            print(f"Error during audio playback: {e}")
                        finally:
                            # 3. Clean up the temporary file
                            if os.path.exists(TEMP_AUDIO_FILENAME):
                                os.remove(TEMP_AUDIO_FILENAME)

                    # Reset buffer for the next message
                    mp3_buffer = io.BytesIO()

    except websockets.exceptions.ConnectionClosed:
        print("Listener: Connection closed.")
    except Exception as e:
        print(f"An error occurred in the audio listener: {e}")


async def send_text_input(websocket):
    """Prompts for user input in the terminal and sends it to the server."""
    print("🎤 Text input sender started.")
    print("Type a sentence and press Enter to hear it spoken.")
    print("Type 'exit' or 'quit' to close the connection.")

    while True:
        try:
            text_to_send = await aioconsole.ainput("> ")
            if text_to_send.lower() in ['exit', 'quit']:
                break

            message = {"text": text_to_send}
            await websocket.send(json.dumps(message))
            print(f"Sent: '{text_to_send}'")

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"An error occurred while sending text: {e}")
            break
    print("Text input sender finished.")


async def main():
    """
    Main function to connect to WebSocket and run listener/sender tasks.
    """
    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print(f"✅ Successfully connected to server with client ID: {CLIENT_ID}")

            await asyncio.gather(
                listen_for_audio(websocket),
                send_text_input(websocket)
            )

    except ConnectionRefusedError:
        print("\n---")
        print("Error: Connection refused. Please make sure the FastAPI server is running.")
        print("---\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Cleaning up resources...")
        print("Done.")

if __name__ == "__main__":
    # This script requires: pip install aioconsole
    # And mpg123: brew install mpg123
    print("Starting TTS test client...")
    asyncio.run(main())

