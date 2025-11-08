import { useState, useEffect, useRef, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";

const WS_URL = "ws://127.0.0.1:8000/ws/";

export const useVoiceSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const isListeningRef = useRef<boolean>(false);
  const socket = useRef<WebSocket | null>(null);
  const client_id = useRef<string>(uuidv4());
  const audioContext = useRef<AudioContext | null>(null);
  const processor = useRef<ScriptProcessorNode | null>(null);
  const source = useRef<MediaStreamAudioSourceNode | null>(null);
  const keepAliveGain = useRef<GainNode | null>(null);
  const audioQueue = useRef<Uint8Array[]>([]);
  const isPlayingAudio = useRef<boolean>(false);
  const audioElement = useRef<HTMLAudioElement | null>(null);
  const receivingAudio = useRef<boolean>(false);

  const playAudioChunks = useCallback(async (chunks: Uint8Array[]) => {
    if (chunks.length === 0) return;

    console.log(`🔊 Playing ${chunks.length} audio chunks combined`);

    // Concatenate all chunks into a single blob
    const audioBlob = new Blob(chunks, { type: 'audio/mpeg' });
    const audioUrl = URL.createObjectURL(audioBlob);

    // Stop any currently playing audio
    if (audioElement.current) {
      audioElement.current.pause();
      audioElement.current = null;
    }

    const audio = new Audio(audioUrl);
    audioElement.current = audio;

    return new Promise<void>((resolve) => {
      audio.onended = () => {
        console.log("🔊 Audio playback completed");
        URL.revokeObjectURL(audioUrl);
        audioElement.current = null;
        resolve();
      };
      audio.onerror = (e) => {
        console.error("Audio play failed:", e);
        URL.revokeObjectURL(audioUrl);
        audioElement.current = null;
        resolve();
      };
      audio.play().catch(e => {
        console.error("Audio play failed:", e);
        URL.revokeObjectURL(audioUrl);
        resolve();
      });
    });
  }, []);

  const connectSocket = useCallback(() => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      console.log("WebSocket is already connected.");
      return;
    }

    console.log(`Connecting to WebSocket with client ID: ${client_id.current}`);
    socket.current = new WebSocket(`${WS_URL}${client_id.current}`);
    socket.current.binaryType = "arraybuffer";

    socket.current.onopen = () => {
      setIsConnected(true);
      console.log("WebSocket connected");
    };

    socket.current.onclose = (event) => {
      setIsConnected(false);
      console.log("WebSocket disconnected:", event.reason);
    };

    socket.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    }

    socket.current.onmessage = (event) => {
        if (typeof event.data === 'string') {
            try {
              const message = JSON.parse(event.data);
              if (message.text) {
                  console.log("Received transcript:", message.text);
                  setTranscript(message.text);
              }
              if (message.isFinal) {
                  console.log("TTS stream completed, playing audio...");
                  receivingAudio.current = false;
                  // Play all collected audio chunks
                  if (audioQueue.current.length > 0) {
                    const chunks = [...audioQueue.current];
                    audioQueue.current = [];
                    playAudioChunks(chunks);
                  }
              }
            } catch (e) {
              console.error("Failed to parse JSON message:", event.data);
            }
        } else if (event.data instanceof ArrayBuffer) {
            // Handle audio stream from server (binary data)
            console.log("📥 Received audio chunk:", event.data.byteLength, "bytes");
            receivingAudio.current = true;
            audioQueue.current.push(new Uint8Array(event.data));
        }
    };
  }, [playAudioChunks]);

  const disconnectSocket = () => {
    if (socket.current) {
      socket.current.close();
      socket.current = null;
    }
    // Stop any playing audio
    if (audioElement.current) {
      audioElement.current.pause();
      audioElement.current = null;
    }
    // Clear audio queue
    audioQueue.current = [];
    stopListening();
  }

  const startListening = useCallback(async () => {
    if (!socket.current || socket.current.readyState !== WebSocket.OPEN) {
      console.log("Socket not connected. Please connect first.");
      // Attempt to connect, and wait a moment before proceeding.
      connectSocket();
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (!socket.current || socket.current.readyState !== WebSocket.OPEN) {
        console.error("Failed to establish WebSocket connection.");
        return;
      }
    }

    if (isListening) {
      console.log("Already listening.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContext) {
          console.error("Browser does not support Web Audio API");
          return;
      }
      audioContext.current = new AudioContext({sampleRate: 16000});
      console.log("AudioContext sampleRate:", audioContext.current.sampleRate);
      source.current = audioContext.current.createMediaStreamSource(stream);

      keepAliveGain.current = audioContext.current.createGain();
      keepAliveGain.current.gain.value = 0.0;

      processor.current = audioContext.current.createScriptProcessor(4096, 1, 1);

      processor.current.onaudioprocess = (e) => {
        if (!isListeningRef.current || !socket.current || socket.current.readyState !== WebSocket.OPEN) {
          return;
        }
        const inputData = e.inputBuffer.getChannelData(0);
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = inputData[i] * 32767;
        }
        console.log("Sending audio chunk:", pcmData.length, "samples");
        socket.current.send(pcmData.buffer);
      };

      source.current.connect(processor.current);
      processor.current.connect(keepAliveGain.current); // Removed to prevent audio feedback
      keepAliveGain.current.connect(audioContext.current.destination);
      setIsListening(true);
      isListeningRef.current = true;
      console.log("Started listening");

    } catch (error) {
      console.error("Error starting listening:", error);
    }
  }, [isListening, connectSocket]);

  const stopListening = useCallback(() => {
    if (!isListening) return;

    setIsListening(false);
    isListeningRef.current = false;
    if (source.current) {
      source.current.disconnect();
      source.current = null;
    }
    if (processor.current) {
      processor.current.disconnect();
      processor.current = null;
    }
    if (audioContext.current) {
      audioContext.current.close();
      audioContext.current = null;
    }
    console.log("Stopped listening");
  }, [isListening]);


  useEffect(() => {
    // Cleanup on unmount
    return () => {
      disconnectSocket();
    };
  }, []);


  const sendText = (text: string) => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      console.log("Sending text:", text);
      socket.current.send(JSON.stringify({ text }));
    } else {
      console.error("Cannot send text, WebSocket is not connected.");
    }
  };

  return {
    isConnected,
    transcript,
    isListening,
    startListening,
    stopListening,
    sendText,
    connectSocket,
  };
};

