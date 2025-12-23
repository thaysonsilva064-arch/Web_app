
import React, { useState } from 'react';

interface PasswordModalProps {
  type: 'main' | 'admin';
  onClose: () => void;
  onConfirm: (password: string) => void;
}

const PasswordModal: React.FC<PasswordModalProps> = ({ type, onClose, onConfirm }) => {
  const [pwd, setPwd] = useState('');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl w-full max-w-sm shadow-2xl animate-in fade-in zoom-in duration-200">
        <h3 className="text-xl font-bold mb-4 text-center">
          {type === 'main' ? 'Senha do Painel' : 'Acesso Restrito Admin'}
        </h3>
        <p className="text-slate-400 text-sm mb-6 text-center">
          Digite a senha para continuar.
        </p>
        <input
          type="password"
          autoFocus
          value={pwd}
          onChange={(e) => setPwd(e.target.value)}
          placeholder="Digite a senha..."
          className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-center text-lg tracking-widest focus:ring-2 focus:ring-indigo-500 outline-none mb-6"
          onKeyDown={(e) => e.key === 'Enter' && onConfirm(pwd)}
        />
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-800 hover:bg-slate-700 py-2 rounded-lg font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => onConfirm(pwd)}
            className="flex-1 bg-indigo-600 hover:bg-indigo-500 py-2 rounded-lg font-bold transition-colors"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};

export default PasswordModal;
