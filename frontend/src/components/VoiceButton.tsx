import { Mic, MicOff } from "lucide-react";
import { Button } from "./ui/button";

interface VoiceButtonProps {
  isListening: boolean;
  onClick: () => void;
}

const VoiceButton = ({ isListening, onClick }: VoiceButtonProps) => {
  return (
    <div className="relative">
      {isListening && (
        <>
          <div className="absolute inset-0 rounded-full bg-primary/30 animate-wave" />
          <div className="absolute inset-0 rounded-full bg-primary/20 animate-wave" style={{ animationDelay: "0.5s" }} />
        </>
      )}
      <Button
        size="lg"
        onClick={onClick}
        className={`
          relative z-10 h-32 w-32 rounded-full text-lg font-semibold
          transition-all duration-300 shadow-xl
          ${isListening 
            ? 'bg-gradient-to-br from-primary to-secondary hover:from-primary/90 hover:to-secondary/90' 
            : 'bg-gradient-to-br from-primary to-secondary hover:from-primary/90 hover:to-secondary/90'
          }
        `}
      >
        {isListening ? (
          <MicOff className="h-12 w-12" />
        ) : (
          <Mic className="h-12 w-12" />
        )}
      </Button>
    </div>
  );
};

export default VoiceButton;
