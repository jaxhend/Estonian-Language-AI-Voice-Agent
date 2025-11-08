import { Card } from "./ui/card";

interface TranscriptDisplayProps {
  transcript: string;
  intent?: {
    name?: string;
    time?: string;
    service?: string;
    location?: string;
  };
}

const TranscriptDisplay = ({ transcript, intent }: TranscriptDisplayProps) => {
  if (!transcript && !intent) return null;

  return (
    <div className="w-full max-w-2xl space-y-4 animate-fade-in">
      {transcript && (
        <Card className="p-6 shadow-[var(--shadow-card)]">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">You said:</h3>
          <p className="text-lg text-foreground">{transcript}</p>
        </Card>
      )}
      
      {intent && Object.keys(intent).length > 0 && (
        <Card className="p-6 shadow-[var(--shadow-card)] border-primary/20">
          <h3 className="text-sm font-medium text-muted-foreground mb-4">Extracted Information:</h3>
          <div className="space-y-2">
            {intent.name && (
              <div className="flex gap-2">
                <span className="text-sm font-medium text-primary">Name:</span>
                <span className="text-sm text-foreground">{intent.name}</span>
              </div>
            )}
            {intent.time && (
              <div className="flex gap-2">
                <span className="text-sm font-medium text-primary">Time:</span>
                <span className="text-sm text-foreground">{intent.time}</span>
              </div>
            )}
            {intent.service && (
              <div className="flex gap-2">
                <span className="text-sm font-medium text-primary">Service:</span>
                <span className="text-sm text-foreground">{intent.service}</span>
              </div>
            )}
            {intent.location && (
              <div className="flex gap-2">
                <span className="text-sm font-medium text-primary">Location:</span>
                <span className="text-sm text-foreground">{intent.location}</span>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default TranscriptDisplay;
