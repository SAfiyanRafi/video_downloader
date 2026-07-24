import React, { useState } from 'react';
import { Video, Layers, Settings2, Play, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import type { QualityOption } from '../types/job';

interface JobFormProps {
  onSubmit: (url: string, parts: number, quality: QualityOption) => void;
  isLoading: boolean;
  error?: string | null;
}

export const JobForm: React.FC<JobFormProps> = ({ onSubmit, isLoading, error }) => {
  const [url, setUrl] = useState('');
  const [parts, setParts] = useState(4);
  const [quality, setQuality] = useState<QualityOption>('best');
  const [urlTouched, setUrlTouched] = useState(false);

  const isValidYoutubeUrl = (u: string) => {
    return /^https?:\/\/(www\.|m\.)?(youtube\.com|youtu\.be)\/.+/i.test(u.trim());
  };

  const isUrlValid = isValidYoutubeUrl(url);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUrlTouched(true);
    if (!isUrlValid) return;
    onSubmit(url.trim(), parts, quality);
  };

  const presetParts = [2, 4, 6, 8, 10, 12, 16, 20];

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>High-Speed Lossless Video Splitter</span>
        </div>
        <h1 className="font-heading text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-3">
          Split Any YouTube Video Into <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-500 via-pink-500 to-amber-400">Equal Parts</span>
        </h1>
        <p className="text-gray-400 text-base sm:text-lg max-w-2xl mx-auto font-normal">
          Paste a video link, select segment count, and instantly generate individual high-definition MP4 clips & ZIP archive without re-encoding quality loss.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6 shadow-2xl border border-gray-800">
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start space-x-3 text-red-400 text-sm">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Unable to process request</p>
              <p className="text-red-300 text-xs mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* YouTube URL Input */}
        <div>
          <label className="block text-sm font-semibold text-gray-200 mb-2 flex items-center justify-between">
            <span className="flex items-center space-x-2">
              <Video className="w-4 h-4 text-red-500" />
              <span>YouTube Video URL</span>
            </span>
            {urlTouched && isUrlValid && (
              <span className="text-xs text-emerald-400 flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Valid YouTube Link</span>
              </span>
            )}
          </label>
          <div className="relative">
            <input
              type="text"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (!urlTouched) setUrlTouched(true);
              }}
              placeholder="https://www.youtube.com/watch?v=..."
              className={`w-full px-4 py-3.5 rounded-xl bg-slate-900/90 border ${
                urlTouched && !isUrlValid && url
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-gray-700/80 focus:border-rose-500 focus:ring-rose-500'
              } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-all font-mono text-sm`}
            />
          </div>
          {urlTouched && !isUrlValid && url && (
            <p className="text-xs text-red-400 mt-1.5 flex items-center space-x-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Please enter a valid YouTube URL (e.g. youtube.com/watch?v=... or youtu.be/...)</span>
            </p>
          )}

          {/* Quick Demo URLs */}
          <div className="mt-2.5 flex items-center space-x-2 text-xs text-gray-400">
            <span className="text-gray-500">Quick Test Link:</span>
            <button
              type="button"
              onClick={() => {
                setUrl('https://www.youtube.com/watch?v=aqz-KE-bpKQ');
                setUrlTouched(true);
              }}
              className="text-rose-400 hover:text-rose-300 underline font-mono text-[11px]"
            >
              Big Buck Bunny Demo
            </button>
          </div>
        </div>

        {/* Split Parts Config */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-semibold text-gray-200 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-pink-400" />
              <span>Number of Equal Parts</span>
            </label>
            <span className="px-3 py-1 rounded-lg bg-rose-500/20 text-rose-300 font-mono font-bold text-sm border border-rose-500/30">
              {parts} Parts
            </span>
          </div>

          {/* Preset Buttons */}
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-2 mb-3">
            {presetParts.map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => setParts(num)}
                className={`py-2 rounded-lg font-mono text-xs font-semibold transition-all ${
                  parts === num
                    ? 'bg-gradient-to-r from-rose-600 to-pink-600 text-white shadow-lg shadow-rose-600/30 ring-2 ring-rose-400/50'
                    : 'bg-slate-900 border border-gray-800 text-gray-300 hover:border-gray-700 hover:text-white'
                }`}
              >
                {num}
              </button>
            ))}
          </div>

          {/* Slider */}
          <input
            type="range"
            min="2"
            max="50"
            value={parts}
            onChange={(e) => setParts(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-rose-500"
          />
          <div className="flex justify-between text-[11px] text-gray-500 font-mono mt-1">
            <span>Min: 2 Parts</span>
            <span>Max: 50 Parts</span>
          </div>
        </div>

        {/* Quality Config */}
        <div>
          <label className="block text-sm font-semibold text-gray-200 mb-2 flex items-center space-x-2">
            <Settings2 className="w-4 h-4 text-amber-400" />
            <span>Video Resolution Quality</span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'best', label: 'Best Quality', desc: 'Original Resolution' },
              { id: '1080p', label: '1080p Full HD', desc: '1920x1080' },
              { id: '720p', label: '720p HD', desc: '1280x720' },
              { id: 'audio_only', label: 'Audio Only', desc: 'MP3/M4A Extract' },
            ].map((q) => (
              <button
                key={q.id}
                type="button"
                onClick={() => setQuality(q.id as QualityOption)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  quality === q.id
                    ? 'bg-rose-500/15 border-rose-500 text-white ring-1 ring-rose-500/50'
                    : 'bg-slate-900/60 border-gray-800 text-gray-400 hover:border-gray-700 hover:text-gray-200'
                }`}
              >
                <div className="text-xs font-bold text-gray-200">{q.label}</div>
                <div className="text-[10px] text-gray-500 mt-0.5">{q.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || (urlTouched && !isUrlValid)}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-rose-600 via-pink-600 to-rose-500 hover:from-rose-500 hover:to-pink-500 text-white font-heading font-bold text-base shadow-xl shadow-rose-600/25 hover:shadow-rose-600/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 group"
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Starting Video Pipeline...</span>
            </div>
          ) : (
            <>
              <span>Start Lossless Video Split</span>
              <Play className="w-4 h-4 fill-white transition-transform group-hover:translate-x-1" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
