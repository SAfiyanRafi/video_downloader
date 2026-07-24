import React from 'react';
import { Scissors, Cpu, ShieldCheck } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-gray-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-18 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-pink-500 flex items-center justify-center shadow-lg shadow-rose-600/30">
            <Scissors className="w-5 h-5 text-white transform -rotate-12" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-heading font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400">
                SplitTube Pro
              </span>
              <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                v1.0 Lossless
              </span>
            </div>
            <p className="text-xs text-gray-400 font-medium">YouTube Video Segment Engine</p>
          </div>
        </div>

        <div className="hidden md:flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-gray-900/80 border border-gray-800 text-xs text-gray-300">
            <Cpu className="w-3.5 h-3.5 text-pink-400" />
            <span>MCP Ready</span>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Stream-Copy FFmpeg</span>
          </div>
        </div>
      </div>
    </header>
  );
};
