
import React, { useState, useEffect } from 'react';
import { User, Config } from '../types';
import { firebaseService } from '../services/firebaseService';

interface AdminPanelProps {
  onBack: () => void;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onBack }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [config, setConfig] = useState<Config>({ mainPassword: '', adminPassword: '' });
  const [mainPwd, setMainPwd] = useState('');
  const [adminPwd, setAdminPwd] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const u = await firebaseService.getAllUsers();
      const c = await firebaseService.getConfig();
      setUsers(u);
      setConfig(c);
      setMainPwd(c.mainPassword);
      setAdminPwd(c.adminPassword);
      setLoading(false);
    };
    fetchData();
  }, []);

  const handleUpdate = async () => {
    await firebaseService.updateConfig({ mainPassword: mainPwd, adminPassword: adminPwd });
    alert('Configurações salvas no Cloud Firestore!');
  };

  const handleBan = async (userId: string) => {
    const reason = prompt('Motivo do Banimento:', 'Violação dos Termos');
    if (reason) {
      await firebaseService.banUser(userId, reason);
      alert('Usuário banido em tempo real!');
    }
  };

  const handleUnban = async (userId: string) => {
    await firebaseService.unbanUser(userId);
    alert('Usuário desbanido!');
  };

  if (loading) return <div className="text-white font-black animate-pulse">CARREGANDO FIREBASE...</div>;

  return (
    <div className="w-full max-w-6xl p-6 space-y-8 animate-in slide-in-from-right-10 duration-700">
      <div className="flex justify-between items-center">
        <h1 className="text-5xl font-black italic tracking-tighter text-white">MASTER <span className="text-red-600">ADMIN</span></h1>
        <button onClick={onBack} className="bg-red-600 hover:bg-red-500 px-8 py-3 rounded-full font-black shadow-xl transition-all">SAIR</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configurações de Senha */}
        <div className="bg-slate-900 p-8 rounded-[3rem] border border-slate-800 shadow-2xl space-y-6 h-fit">
          <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-4">Configurações</h3>
          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase">Senha Principal</label>
              <input type="text" value={mainPwd} onChange={e => setMainPwd(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-white outline-none focus:border-red-600"/>
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase">Senha Admin</label>
              <input type="text" value={adminPwd} onChange={e => setAdminPwd(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-white outline-none focus:border-red-600"/>
            </div>
            <button onClick={handleUpdate} className="w-full bg-white text-black py-4 rounded-2xl font-black hover:bg-slate-200 transition-all mt-4">SALVAR NO BANCO</button>
          </div>
        </div>

        {/* Lista de Usuários */}
        <div className="lg:col-span-2 bg-slate-900 rounded-[3rem] border border-slate-800 shadow-2xl overflow-hidden">
          <div className="p-8 bg-slate-800/30 flex justify-between items-center">
             <h3 className="font-black text-white uppercase tracking-tighter">Gerenciar Usuários</h3>
             <span className="text-xs bg-red-600 text-white px-3 py-1 rounded-full font-bold">{users.length} TOTAL</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="text-[10px] text-slate-500 uppercase font-black bg-slate-950/50">
                <tr>
                  <th className="px-8 py-4">Usuário</th>
                  <th className="px-8 py-4">Login</th>
                  <th className="px-8 py-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {users.map(u => (
                  <tr key={u.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-8 py-6">
                      <p className="font-black text-white">{u.name}</p>
                      <p className="text-[10px] text-slate-500 uppercase">{u.email}</p>
                    </td>
                    <td className="px-8 py-6 text-xs text-slate-400 font-mono">{u.loginTime}</td>
                    <td className="px-8 py-6 text-right space-x-2">
                      <button onClick={() => handleBan(u.id)} className="bg-red-600/10 text-red-500 px-4 py-2 rounded-xl text-[10px] font-black hover:bg-red-600 hover:text-white transition-all">BANIR</button>
                      <button onClick={() => handleUnban(u.id)} className="bg-emerald-600/10 text-emerald-500 px-4 py-2 rounded-xl text-[10px] font-black hover:bg-emerald-600 hover:text-white transition-all">DESBANIR</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
