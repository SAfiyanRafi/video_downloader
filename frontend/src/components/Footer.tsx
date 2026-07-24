import React from 'react';
import { Sparkles, Cpu, ShieldAlert } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-20 border-t border-gray-800/80 bg-slate-950/80 py-10 text-xs text-gray-400">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center border border-rose-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <p className="text-gray-200 font-semibold">YouTube Video Splitter Platform</p>
            <p className="text-gray-400 text-[11px]">Production-Ready Modular Architecture (FastAPI + React)</p>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-gray-400">
          <span className="flex items-center space-x-1 hover:text-gray-200 cursor-pointer">
            <Cpu className="w-3.5 h-3.5 text-pink-400" />
            <span>MCP Protocol Enabled</span>
          </span>
          <span className="flex items-center space-x-1 hover:text-gray-200 cursor-pointer">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>Legal Content Only</span>
          </span>
        </div>

        <div className="text-[11px] text-gray-400">
          © 2026 SplitTube Pro. All rights reserved.
        </div>
      </div>
    </footer>
  );
};
