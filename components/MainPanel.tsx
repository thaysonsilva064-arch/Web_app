
import React, { useState } from 'react';

interface MainPanelProps {
  onBack: () => void;
}

const MainPanel: React.FC<MainPanelProps> = ({ onBack }) => {
  const [uid, setUid] = useState('');
  const [codeTeam, setCodeTeam] = useState('');
  const [maxGame, setMaxGame] = useState('10');
  const [loading, setLoading] = useState(false);

  const apiRequest = async (url: string) => {
    setLoading(true);
    try {
      // Usamos modo no-cors se o servidor for apenas um trigger, 
      // mas o ideal é que o servidor suporte CORS.
      await fetch(url, { mode: 'no-cors' });
      alert('Requisição enviada com sucesso!');
    } catch (e) {
      alert('Erro ao enviar requisição. Verifique o servidor local.');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (type: 'like' | 'friend' | 'spam' | 'stop') => {
    if (!uid && type !== 'stop') return alert('Coloque o UID primeiro!');
    
    let url = '';
    const target = uid.trim();
    
    switch(type) {
      case 'like': url = `http://192.168.3.39:5000/like_all?uid_alvo=${target}`; break;
      case 'friend': url = `http://192.168.3.39:5000/add_friend?uid_alvo=${target}`; break;
      case 'spam': url = `http://192.168.3.39:5000/spam?uid_alvo=${target}`; break;
      case 'stop': url = `http://192.168.3.39:5000/stop_spam`; break;
    }
    apiRequest(url);
  };

  const handleStart = () => {
    if (!codeTeam) return alert('Código da sala obrigatório!');
    const url = `http://192.168.3.39:5000/start?codeteam=${codeTeam}&maxgame=${maxGame}`;
    apiRequest(url);
  };

  return (
    <div className="w-full max-w-5xl p-4 grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in zoom-in duration-500">
      
      {/* Coluna de Ações Rápidas */}
      <div className="bg-slate-900/60 backdrop-blur-md p-8 rounded-[3rem] border border-slate-800 shadow-2xl space-y-8">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-black text-white italic">CONSOLE <span className="text-indigo-500">PRO</span></h2>
          <button onClick={onBack} className="text-xs bg-slate-800 px-4 py-2 rounded-full font-bold hover:bg-slate-700 transition-all border border-slate-700">VOLTAR</button>
        </div>

        <div className="space-y-4">
          <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">ID do Alvo</label>
          <input 
            type="text" 
            value={uid} 
            onChange={e => setUid(e.target.value)}
            placeholder="Digite o UID..."
            className="w-full bg-slate-950 border-2 border-slate-800 rounded-2xl p-4 text-white focus:border-indigo-600 outline-none transition-all shadow-inner font-mono"
          />
        </div>

        <div className="grid grid-cols-1 gap-3">
          <button onClick={() => handleAction('like')} className="bg-indigo-600 hover:bg-indigo-500 py-4 rounded-2xl font-black shadow-lg shadow-indigo-500/20 transform hover:-translate-y-1 transition-all">VISITAR PERFIL & LIKES</button>
          <button onClick={() => handleAction('friend')} className="bg-slate-800 hover:bg-slate-700 py-4 rounded-2xl font-black transition-all">PEDIDO DE AMIZADE</button>
          <button onClick={() => handleAction('spam')} className="bg-orange-600 hover:bg-orange-500 py-4 rounded-2xl font-black shadow-lg shadow-orange-500/20 transform hover:-translate-y-1 transition-all">CHAMAR PARA JOGAR (SPAM)</button>
          <button onClick={() => handleAction('stop')} className="bg-red-600 hover:bg-red-500 py-4 rounded-2xl font-black shadow-lg shadow-red-500/20 transition-all uppercase text-sm">Parar Tudo</button>
        </div>
      </div>

      {/* Coluna de Partidas */}
      <div className="bg-slate-900/60 backdrop-blur-md p-8 rounded-[3rem] border border-slate-800 shadow-2xl flex flex-col justify-between">
        <div className="space-y-8">
          <h2 className="text-2xl font-black text-white italic text-center">GAME <span className="text-emerald-500">BOOST</span></h2>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Código da Sala</label>
              <input 
                type="text" 
                value={codeTeam} 
                onChange={e => setCodeTeam(e.target.value)}
                placeholder="Ex: 827364"
                className="w-full bg-slate-950 border-2 border-slate-800 rounded-2xl p-4 text-center text-xl font-black text-emerald-400 focus:border-emerald-600 outline-none transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Quantidade de Partidas</label>
              <input 
                type="number" 
                value={maxGame} 
                onChange={e => setMaxGame(e.target.value)}
                className="w-full bg-slate-950 border-2 border-slate-800 rounded-2xl p-4 text-center font-bold text-white focus:border-indigo-600 outline-none"
              />
            </div>
          </div>
        </div>

        <button 
          onClick={handleStart}
          disabled={loading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 py-6 rounded-[2rem] font-black text-lg shadow-lg shadow-emerald-500/20 transform hover:scale-[1.02] active:scale-95 transition-all mt-8"
        >
          {loading ? 'PROCESSANDO...' : 'INICIAR PARTIDAS'}
        </button>
      </div>
    </div>
  );
};

export default MainPanel;
