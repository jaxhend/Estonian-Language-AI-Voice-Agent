import { useState, useEffect } from "react";
import VoiceButton from "@/components/VoiceButton";
import VoiceVisualizer from "@/components/VoiceVisualizer";
import TranscriptDisplay from "@/components/TranscriptDisplay";
import ConversationHistory from "@/components/ConversationHistory";
import Navbar from "@/components/Navbar";
import { useVoiceSocket } from "@/hooks/use-voice-socket";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const Voice = () => {
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    connectSocket,
    sendText,
      messages,
  } = useVoiceSocket();
  const [intent, setIntent] = useState<any>(null);

  useEffect(() => {
    connectSocket();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  };

  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
      if (transcript) {
        sendText(transcript);
      }
    } else {
      startListening();
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex flex-col items-center p-6 py-12 gap-12">
        <div className="w-full max-w-4xl flex flex-col items-center gap-8">
          <div className="text-center space-y-2 animate-fade-in">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Estonian AI Voice Assistant
            </h1>
            <p className="text-lg text-muted-foreground">
              Press the button and tell me how I can help you
            </p>
          </div>

          <VoiceButton isListening={isListening} onClick={handleVoiceClick} />

          <VoiceVisualizer isActive={isListening} />

          <TranscriptDisplay transcript={transcript} intent={intent} />
        </div>

        <ConversationHistory messages={messages} />
      </div>
    </div>
  );
};

export default Voice;
