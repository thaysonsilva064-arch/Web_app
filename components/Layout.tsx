
import React from 'react';
import { User } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  user?: User | null;
  onLogout?: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, user, onLogout }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-slate-950">
      <header className="w-full max-w-4xl flex justify-between items-center mb-8 px-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          BotMaster Hub
        </h1>
        {user && (
          <div className="flex items-center gap-4 bg-slate-900 p-2 px-4 rounded-full border border-slate-800 shadow-xl">
            <div className="flex flex-col">
              <span className="text-sm font-medium text-slate-200">{user.name}</span>
              <span className="text-xs text-slate-500">{user.email}</span>
            </div>
            <button 
              onClick={onLogout}
              className="text-xs bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white px-3 py-1 rounded transition-all duration-300 border border-red-500/20"
            >
              Sair
            </button>
          </div>
        )}
      </header>
      <main className="w-full flex justify-center items-center">
        {children}
      </main>
      <footer className="mt-auto py-6 text-slate-600 text-xs text-center w-full">
        &copy; 2024 BotMaster Automation Services. All rights reserved.
      </footer>
    </div>
  );
};

export default Layout;
