import React from 'react';
import { Sparkles, Cpu, ShieldAlert, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-16 sm:mt-24 border-t border-gray-800/80 bg-slate-950/90 py-8 sm:py-12 text-xs text-gray-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
        {/* Brand Summary */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center border border-rose-500/30 shrink-0">
            <Sparkles className="w-4.5 h-4.5" />
          </div>
          <div>
            <p className="text-gray-200 font-bold text-sm">YouTube Video Splitter Platform</p>
            <p className="text-gray-400 text-xs mt-0.5">Mobile-First, Production-Ready SaaS Architecture</p>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap justify-center items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-300">
            <Cpu className="w-3.5 h-3.5 text-pink-400 shrink-0" />
            <span>MCP Protocol Enabled</span>
          </span>
          <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-300">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Authorized Content Only</span>
          </span>
        </div>

        {/* Copyright */}
        <div className="text-xs text-gray-400 flex items-center space-x-1">
          <span>© 2026 SplitTube Pro. Built with</span>
          <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
        </div>
      </div>
    </footer>
  );
};
