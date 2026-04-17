import { useState } from 'react';
import { useAuth, logout } from 'wasp/client/auth';

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const { data: user } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <aside 
      className={`fixed top-0 left-0 h-full bg-secondary border-r border-border transition-all duration-300 z-50 ${
        isOpen ? 'w-64' : 'w-0 overflow-hidden'
      } md:relative md:w-64 md:translate-x-0`}
    >
      <div className="flex flex-col h-full p-4">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl font-black tracking-tighter">VIBE2BLENDER</h1>
          <button 
            onClick={() => setIsOpen(false)}
            className="md:hidden text-text hover:text-accent"
          >
            ✕
          </button>
        </div>
        
        <button className="w-full py-2 px-4 border border-border bg-bg hover:bg-accent transition-colors text-[10px] font-black tracking-widest mb-6 flex items-center justify-center gap-2">
          NEW_PROJECT
        </button>

        <nav className="flex-1 overflow-y-auto">
          <div className="text-[9px] text-accent uppercase font-black mb-4 tracking-widest opacity-50">
            SESSION_HISTORY
          </div>
          <div className="space-y-1">
            <div className="p-3 text-[10px] border border-border bg-bg/50 text-accent grayscale italic">
              NO_SAVED_SCRIPTS
            </div>
          </div>
        </nav>

        <div className="mt-auto pt-4 border-t border-border">
          <div className="flex items-center justify-between gap-3 p-2 bg-bg/20 rounded">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-text text-bg rounded-none flex items-center justify-center text-[10px] font-black">
                {user?.username?.substring(0, 2).toUpperCase() || '??'}
              </div>
              <div className="text-[10px] truncate font-black tracking-tighter uppercase">{user?.username}</div>
            </div>
            <button 
              onClick={handleLogout}
              className="text-[9px] font-black text-accent hover:text-text transition-colors"
            >
              LOGOUT
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};
