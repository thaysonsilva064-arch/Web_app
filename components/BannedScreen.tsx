
import React, { useState, useEffect } from 'react';

interface BannedScreenProps {
  reason: string;
  onFinish: () => void;
}

const BannedScreen: React.FC<BannedScreenProps> = ({ reason, onFinish }) => {
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(prev => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      onFinish();
    }
  }, [countdown, onFinish]);

  return (
    <div className="w-full max-w-lg bg-black/80 border border-red-500/50 p-12 rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.2)] text-center space-y-8 animate-pulse">
      <div className="w-24 h-24 bg-red-500/20 border-4 border-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      
      <div className="space-y-4">
        <h2 className="text-4xl font-black text-red-500 tracking-tighter uppercase italic">VOCÊ FOI BANIDO</h2>
        <div className="bg-red-500/10 p-4 rounded-lg border border-red-500/20">
          <p className="text-slate-300 font-medium">Motivo: <span className="text-white">{reason}</span></p>
        </div>
      </div>

      <div className="pt-8 space-y-2">
        <p className="text-slate-500 text-sm uppercase font-bold tracking-widest">Saindo em</p>
        <div className="text-6xl font-black text-white">{countdown}</div>
        <p className="text-xs text-red-400/50">404 NOT FOUND</p>
      </div>
    </div>
  );
};

export default BannedScreen;
