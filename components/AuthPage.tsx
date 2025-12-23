
import React, { useState } from 'react';
import { User, View } from '../types';
import PasswordModal from './PasswordModal';
import { firebaseService } from '../services/firebaseService';

interface AuthPageProps {
  user: User | null;
  onLoginSuccess: (user: User) => void;
  onNavigate: (view: View) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ user, onLoginSuccess, onNavigate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalType, setModalType] = useState<'main' | 'admin' | null>(null);

  const handleLogin = async (provider: 'google' | 'github') => {
    setLoading(true);
    setError(null);
    try {
      const userData = await firebaseService.login(provider);
      onLoginSuccess(userData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAccessRequest = (type: 'main' | 'admin') => {
    setModalType(type);
  };

  const handlePasswordConfirm = async (password: string) => {
    const config = await firebaseService.getConfig();
    if (modalType === 'main') {
      if (password === config.mainPassword) onNavigate(View.MAIN_PANEL);
      else alert('Senha incorreta!');
    } else if (modalType === 'admin') {
      if (password === config.adminPassword) onNavigate(View.ADMIN_PANEL);
      else alert('Senha incorreta!');
    }
    setModalType(null);
  };

  return (
    <div className="perspective-1000 w-full max-w-md">
      <div className="bg-slate-900/80 backdrop-blur-xl p-10 rounded-[2.5rem] border border-slate-700/50 shadow-[0_20px_50px_rgba(0,0,0,0.5)] transform hover:rotate-x-2 hover:rotate-y-2 transition-all duration-500 space-y-8 border-t-white/10">
        <div className="text-center space-y-3">
          <div className="inline-block p-4 rounded-3xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg mb-2">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <h2 className="text-4xl font-black tracking-tighter text-white">ACCESS HUB</h2>
          <p className="text-slate-400 font-medium">Automação de alta performance</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-2xl text-red-400 text-xs text-center font-bold">
            {error}
          </div>
        )}

        {!user ? (
          <div className="space-y-4">
            <button
              disabled={loading}
              onClick={() => handleLogin('google')}
              className="w-full flex items-center justify-center gap-3 bg-white text-slate-950 py-4 rounded-2xl font-black hover:scale-[1.02] transition-all active:scale-95 disabled:opacity-50 shadow-xl"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google Login
            </button>

            <button
              disabled={loading}
              onClick={() => handleLogin('github')}
              className="w-full flex items-center justify-center gap-3 bg-slate-950 text-white py-4 rounded-2xl font-black hover:scale-[1.02] transition-all active:scale-95 disabled:opacity-50 border border-slate-800 shadow-xl"
            >
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
              </svg>
              GitHub Login
            </button>
          </div>
        ) : (
          <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl">
               <p className="text-center text-emerald-400 text-sm font-black uppercase tracking-widest">Sessão Ativa</p>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              <button
                onClick={() => handleAccessRequest('main')}
                className="group relative overflow-hidden bg-gradient-to-r from-indigo-600 to-indigo-500 text-white py-5 rounded-[1.5rem] font-black transition-all shadow-[0_10px_30px_rgba(79,70,229,0.4)] hover:-translate-y-1 active:scale-95"
              >
                ACESSAR PAINEL PRINCIPAL
              </button>

              <button
                onClick={() => handleAccessRequest('admin')}
                className="bg-slate-800/50 hover:bg-slate-800 text-slate-400 py-4 rounded-[1.5rem] font-bold transition-all border border-slate-700/50 hover:text-white"
              >
                CONTROLE ADMINISTRATIVO
              </button>
            </div>
          </div>
        )}
      </div>

      {modalType && (
        <PasswordModal 
          type={modalType} 
          onClose={() => setModalType(null)} 
          onConfirm={handlePasswordConfirm} 
        />
      )}
    </div>
  );
};

export default AuthPage;
