import React, { useState } from 'react';
import { Scissors, Cpu, ShieldCheck, Menu, X, Code2, BookOpen } from 'lucide-react';

export const Header: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="border-b border-gray-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between">
        {/* Brand Logo & Title */}
        <a 
          href="/" 
          className="flex items-center space-x-3 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 rounded-xl p-1"
          aria-label="SplitTube Pro Home"
        >
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-tr from-rose-600 via-pink-600 to-amber-500 flex items-center justify-center shadow-lg shadow-rose-600/30 group-hover:scale-105 transition-transform">
            <Scissors className="w-5 h-5 sm:w-6 sm:h-6 text-white transform -rotate-12" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-heading font-extrabold text-lg sm:text-xl md:text-2xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-100 to-gray-400">
                SplitTube Pro
              </span>
              <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                Lossless
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-gray-400 font-medium hidden sm:block">
              YouTube Video Splitter Platform
            </p>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-4 lg:space-x-6">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 text-xs font-semibold text-gray-300 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-slate-900 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none"
          >
            <BookOpen className="w-4 h-4 text-rose-400" />
            <span>API Specs</span>
          </a>

          <a
            href="https://github.com/SAfiyanRafi/video_downloader"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 text-xs font-semibold text-gray-300 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-slate-900 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none"
          >
            <Code2 className="w-4 h-4 text-gray-300" />
            <span>GitHub</span>
          </a>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-gray-900/90 border border-gray-800 text-xs text-gray-300">
            <Cpu className="w-3.5 h-3.5 text-pink-400 shrink-0" />
            <span className="font-mono">MCP Protocol</span>
          </div>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Stream Copy</span>
          </div>
        </nav>

        {/* Mobile Hamburger Toggle Button (Minimum 44x44px touch target) */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden w-11 h-11 flex items-center justify-center rounded-xl bg-slate-900 border border-gray-800 text-gray-300 hover:text-white hover:border-gray-700 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none transition-colors"
          aria-expanded={mobileMenuOpen}
          aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
        >
          {mobileMenuOpen ? <X className="w-6 h-6 text-rose-400" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Collapsible Navigation Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-800 bg-slate-950/95 backdrop-blur-xl px-4 py-5 space-y-4 animate-in slide-in-from-top duration-200">
          <div className="grid grid-cols-1 gap-2">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-slate-900/80 border border-gray-800 text-sm font-semibold text-gray-200 hover:text-white"
            >
              <BookOpen className="w-5 h-5 text-rose-400" />
              <span>Interactive API Specs</span>
            </a>

            <a
              href="https://github.com/SAfiyanRafi/video_downloader"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-slate-900/80 border border-gray-800 text-sm font-semibold text-gray-200 hover:text-white"
            >
              <Code2 className="w-5 h-5 text-gray-300" />
              <span>GitHub Repository</span>
            </a>
          </div>

          <div className="pt-2 border-t border-gray-800/80 flex flex-wrap gap-2 text-xs">
            <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-300">
              <Cpu className="w-4 h-4 text-pink-400" />
              <span>MCP Ready</span>
            </span>
            <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Lossless Stream Copy</span>
            </span>
          </div>
        </div>
      )}
    </header>
  );
};
