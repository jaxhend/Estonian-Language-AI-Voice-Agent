import { useEffect, useState } from "react";

interface VoiceVisualizerProps {
  isActive: boolean;
}

const VoiceVisualizer = ({ isActive }: VoiceVisualizerProps) => {
  const [bars, setBars] = useState<number[]>(Array(20).fill(0.2));

  useEffect(() => {
    if (!isActive) {
      setBars(Array(20).fill(0.2));
      return;
    }

    const interval = setInterval(() => {
      setBars(Array(20).fill(0).map(() => Math.random() * 0.8 + 0.2));
    }, 100);

    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className="flex items-center justify-center gap-1 h-24">
      {bars.map((height, i) => (
        <div
          key={i}
          className="w-2 rounded-full bg-gradient-to-t from-primary to-secondary transition-all duration-100"
          style={{
            height: `${height * 100}%`,
            opacity: isActive ? 1 : 0.3,
          }}
        />
      ))}
    </div>
  );
};

export default VoiceVisualizer;
