import { useState } from "react";
import VoiceButton from "@/components/VoiceButton";
import VoiceVisualizer from "@/components/VoiceVisualizer";
import TranscriptDisplay from "@/components/TranscriptDisplay";
import ConversationHistory from "@/components/ConversationHistory";
import Navbar from "@/components/Navbar";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const Voice = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [intent, setIntent] = useState<any>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const handleVoiceClick = () => {
    setIsListening(!isListening);
    
    // Simulate voice recognition for demo
    if (!isListening) {
      setTimeout(() => {
        const userMessage = "I'd like to book a haircut appointment for tomorrow at 2 PM in downtown location.";
        setTranscript(userMessage);
        
        // Add user message to conversation
        setMessages(prev => [...prev, {
          role: "user",
          content: userMessage,
          timestamp: getCurrentTime()
        }]);
        
        setIntent({
          name: "John Doe",
          time: "Tomorrow at 2:00 PM",
          service: "Haircut",
          location: "Downtown Branch"
        });
        
        // Simulate AI response
        setTimeout(() => {
          const aiResponse = "I understand you'd like to book a haircut appointment. I've extracted the following details: tomorrow at 2:00 PM at our Downtown Branch. Would you like to proceed with this booking?";
          setMessages(prev => [...prev, {
            role: "assistant",
            content: aiResponse,
            timestamp: getCurrentTime()
          }]);
        }, 1000);
        
        setIsListening(false);
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex flex-col items-center p-6 py-12 gap-12">
        <div className="w-full max-w-4xl flex flex-col items-center gap-8">
          <div className="text-center space-y-2 animate-fade-in">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              AI Voice Assistant
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
