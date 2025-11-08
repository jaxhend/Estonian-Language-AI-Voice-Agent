import { Card } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { User, Bot } from "lucide-react";
import {useEffect, useRef} from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ConversationHistoryProps {
  messages: Message[];
}

const ConversationHistory = ({ messages }: ConversationHistoryProps) => {
    if (messages.length === 0) return null;

  return (
    <Card className="w-full max-w-3xl p-6 shadow-[var(--shadow-card)] animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-lg font-semibold text-foreground">Conversation History</h3>
        <span className="text-sm text-muted-foreground">({messages.length} messages)</span>
      </div>
      
      <ScrollArea className="h-[400px] pr-4 [&>[data-radix-scroll-area-viewport]]:overflow-y-scroll [&_[data-radix-scrollbar]]:opacity-100">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.role === "user" ? "flex-row" : "flex-row-reverse"}`}
            >
              <div className={`
                flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center
                ${message.role === "user" 
                  ? "bg-primary/10 text-primary" 
                  : "bg-secondary/10 text-secondary"
                }
              `}>
                {message.role === "user" ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>
              
              <div className={`flex-1 ${message.role === "user" ? "text-left" : "text-right"}`}>
                <div className={`
                  inline-block max-w-[85%] p-3 rounded-lg
                  ${message.role === "user"
                    ? "bg-primary/10 text-foreground"
                    : "bg-secondary/10 text-foreground"
                  }
                `}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
                <p className="text-xs text-muted-foreground mt-1 px-1">{message.timestamp}</p>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
};

export default ConversationHistory;
