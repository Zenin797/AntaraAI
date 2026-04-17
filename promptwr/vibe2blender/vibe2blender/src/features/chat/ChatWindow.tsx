import { useEffect, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const ChatWindow = ({ messages, isTyping }: { messages: Message[], isTyping: boolean }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
      {messages.map((msg, idx) => (
        <div 
          key={idx} 
          className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-fade-in`}
        >
          <div 
            className={`max-w-[85%] p-4 text-xs font-medium leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-transparent border border-text text-text' 
                : 'bg-secondary border border-border text-text'
            }`}
          >
            <div className="text-[9px] font-black uppercase tracking-widest mb-2 opacity-50">
              {msg.role === 'user' ? 'USER_PROMPT' : 'AI_INTERVIEWER'}
            </div>
            {msg.content}
          </div>
        </div>
      ))}
      
      {isTyping && (
        <div className="flex flex-col items-start animate-fade-in">
          <div className="bg-secondary border border-border p-4">
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 bg-text animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-1.5 h-1.5 bg-text animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-1.5 h-1.5 bg-text animate-bounce"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
