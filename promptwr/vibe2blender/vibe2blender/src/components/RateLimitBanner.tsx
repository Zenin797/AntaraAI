import { useState, useEffect } from 'react';

export const RateLimitBanner = ({ isVisible = false, retryAfterSeconds = 0 }) => {
  const [timeLeft, setTimeLeft] = useState(retryAfterSeconds);

  useEffect(() => {
    if (isVisible && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isVisible, timeLeft]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[100] animate-slide-down">
      <div className="bg-text text-bg py-3 px-6 flex items-center justify-between font-bold text-sm tracking-tighter">
        <div className="flex items-center gap-4">
          <span className="bg-bg text-text px-2 py-0.5 rounded text-[10px] animate-pulse">429 ABUSE DETECTED</span>
          <span>TOO MANY REQUESTS. RETRYING IN {timeLeft}S...</span>
        </div>
        <div className="h-1 bg-accent/20 flex-1 mx-8 relative">
          <div 
            className="h-full bg-accent transition-all duration-1000"
            style={{ width: `${(timeLeft / retryAfterSeconds) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};
