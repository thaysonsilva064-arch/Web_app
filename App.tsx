
import React, { useState, useEffect } from 'react';
import { View, User, BanInfo } from './types';
import { firebaseService } from './services/firebaseService';
import AuthPage from './components/AuthPage';
import MainPanel from './components/MainPanel';
import AdminPanel from './components/AdminPanel';
import BannedScreen from './components/BannedScreen';
import Layout from './components/Layout';
import { auth } from './firebase';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>(View.LOGIN);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [banInfo, setBanInfo] = useState<BanInfo | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    // Monitora estado da autenticação
    const unsubscribeAuth = auth.onAuthStateChanged(async (firebaseUser) => {
      if (firebaseUser) {
        const userData: User = {
          id: firebaseUser.uid,
          name: firebaseUser.displayName || 'Usuário',
          email: firebaseUser.email || '',
          provider: 'google', // Simplificado para o tipo
          ip: 'Detectando...',
          loginTime: new Date().toLocaleString()
        };
        setCurrentUser(userData);
        
        // Monitora banimento em tempo real
        const unsubscribeBan = firebaseService.subscribeToBan(firebaseUser.uid, (ban) => {
          if (ban) {
            setBanInfo(ban);
            setCurrentView(View.BANNED);
          } else if (currentView === View.BANNED) {
            setCurrentView(View.LOGIN);
            setBanInfo(null);
          }
        });
        
        return () => unsubscribeBan();
      } else {
        setCurrentUser(null);
        setCurrentView(View.LOGIN);
      }
      setIsInitializing(false);
    });

    return () => unsubscribeAuth();
  }, [currentView]);

  const handleLogout = async () => {
    await firebaseService.logout();
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const renderContent = () => {
    if (currentView === View.BANNED && banInfo) {
      return <BannedScreen reason={banInfo.reason} onFinish={() => handleLogout()} />;
    }

    switch (currentView) {
      case View.LOGIN:
        return (
          <AuthPage 
            onLoginSuccess={(u) => setCurrentUser(u)} 
            user={currentUser} 
            onNavigate={(v) => setCurrentView(v)} 
          />
        );
      case View.MAIN_PANEL:
        return <MainPanel onBack={() => setCurrentView(View.LOGIN)} />;
      case View.ADMIN_PANEL:
        return <AdminPanel onBack={() => setCurrentView(View.LOGIN)} />;
      default:
        return <AuthPage onLoginSuccess={() => {}} user={currentUser} onNavigate={(v) => setCurrentView(v)} />;
    }
  };

  return (
    <Layout onLogout={currentUser ? handleLogout : undefined} user={currentUser}>
      {renderContent()}
    </Layout>
  );
};

export default App;
