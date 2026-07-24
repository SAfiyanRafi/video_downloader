import React, { useState, useEffect } from 'react';
import { Video, Layers, Settings2, Play, Sparkles, CheckCircle2, AlertCircle, Tv, Crop, Smartphone, Monitor, Square, Maximize2 } from 'lucide-react';
import type { QualityOption, AspectRatioOption, ChannelProfile } from '../types/job';
import { fetchChannels } from '../services/api';

interface JobFormProps {
  onSubmit: (url: string, parts: number, quality: QualityOption, aspectRatio: AspectRatioOption, channel?: string) => void;
  isLoading: boolean;
  error?: string | null;
}

export const JobForm: React.FC<JobFormProps> = ({ onSubmit, isLoading, error }) => {
  const [url, setUrl] = useState('');
  const [parts, setParts] = useState(4);
  const [quality, setQuality] = useState<QualityOption>('best');
  const [aspectRatio, setAspectRatio] = useState<AspectRatioOption>('original');
  const [channel, setChannel] = useState<string>('');
  const [channels, setChannels] = useState<ChannelProfile[]>([]);
  const [urlTouched, setUrlTouched] = useState(false);

  useEffect(() => {
    fetchChannels().then((data) => {
      setChannels(data);
    });
  }, []);

  const isValidYoutubeUrl = (u: string) => {
    return /^https?:\/\/(www\.|m\.)?(youtube\.com|youtu\.be)\/.+/i.test(u.trim());
  };

  const isUrlValid = isValidYoutubeUrl(url);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUrlTouched(true);
    if (!isUrlValid) return;
    onSubmit(url.trim(), parts, quality, aspectRatio, channel || undefined);
  };

  const presetParts = [2, 4, 6, 8, 10, 12, 16, 20];

  return (
    <div className="w-full max-w-4xl mx-auto px-0 sm:px-2">
      {/* Title & Hero Section */}
      <div className="text-center mb-6 sm:mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs sm:text-sm font-semibold uppercase tracking-wider mb-3 sm:mb-4">
          <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
          <span>Mobile-First Lossless Splitter</span>
        </div>
        <h1 className="font-heading text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-3 sm:mb-4 leading-tight">
          Split Any Video Into <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-500 via-pink-500 to-amber-400">Equal Parts</span>
        </h1>
        <p className="text-gray-300 text-sm sm:text-base md:text-lg max-w-2xl mx-auto font-normal leading-relaxed px-2">
          Paste a YouTube link, choose your segment count, and download high-definition MP4 clips & ZIP archives instantly without re-encoding quality loss.
        </p>
      </div>

      {/* Main Glassmorphic Responsive Card */}
      <form 
        onSubmit={handleSubmit} 
        className="glass-panel p-5 sm:p-8 lg:p-10 rounded-2xl sm:rounded-3xl space-y-6 sm:space-y-8 shadow-2xl border border-gray-800/80 transition-all"
      >
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start space-x-3 text-red-400 text-xs sm:text-sm">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Unable to process request</p>
              <p className="text-red-300 text-xs mt-0.5 leading-normal">{error}</p>
            </div>
          </div>
        )}

        {/* YouTube URL Input Section */}
        <div className="space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <label htmlFor="youtube-url-input" className="text-xs sm:text-sm font-semibold text-gray-200 flex items-center space-x-2">
              <Video className="w-4 h-4 text-rose-500 shrink-0" />
              <span>YouTube Video URL</span>
            </label>
            {urlTouched && isUrlValid && (
              <span className="text-xs text-emerald-400 flex items-center space-x-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                <span>Valid YouTube Link</span>
              </span>
            )}
          </div>

          <div className="relative">
            <input
              id="youtube-url-input"
              type="url"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (!urlTouched) setUrlTouched(true);
              }}
              placeholder="https://www.youtube.com/watch?v=..."
              className={`w-full min-h-[48px] px-4 py-3 rounded-xl bg-slate-900/90 border ${
                urlTouched && !isUrlValid && url
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-gray-700/80 focus:border-rose-500 focus:ring-rose-500'
              } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-all font-mono text-xs sm:text-sm`}
              aria-invalid={urlTouched && !isUrlValid}
            />
          </div>

          {urlTouched && !isUrlValid && url && (
            <p className="text-xs text-red-400 flex items-center space-x-1 pt-1">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>Please enter a valid YouTube URL (e.g. youtube.com/watch?v=... or youtu.be/...)</span>
            </p>
          )}

          {/* Quick Demo Filler Button */}
          <div className="pt-1 flex items-center space-x-2 text-xs text-gray-400">
            <span className="text-gray-500">Test Link:</span>
            <button
              type="button"
              onClick={() => {
                setUrl('https://www.youtube.com/watch?v=aqz-KE-bpKQ');
                setUrlTouched(true);
              }}
              className="text-rose-400 hover:text-rose-300 underline font-mono text-[11px] min-h-[32px] flex items-center"
            >
              Big Buck Bunny Demo
            </button>
          </div>
        </div>

        {/* Number of Equal Parts Config */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label htmlFor="parts-slider" className="text-xs sm:text-sm font-semibold text-gray-200 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-pink-400 shrink-0" />
              <span>Number of Equal Parts</span>
            </label>
            <span className="px-3 py-1 rounded-lg bg-rose-500/20 text-rose-300 font-mono font-bold text-xs sm:text-sm border border-rose-500/30">
              {parts} Parts
            </span>
          </div>

          {/* Preset Buttons Grid (Responsive 4 cols on mobile, 8 cols on tablet/desktop) */}
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
            {presetParts.map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => setParts(num)}
                className={`min-h-[44px] rounded-xl font-mono text-xs font-bold transition-all flex items-center justify-center ${
                  parts === num
                    ? 'bg-gradient-to-r from-rose-600 to-pink-600 text-white shadow-lg shadow-rose-600/30 ring-2 ring-rose-400/50'
                    : 'bg-slate-900 border border-gray-800 text-gray-300 hover:border-gray-700 hover:text-white'
                } focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none`}
              >
                {num}
              </button>
            ))}
          </div>

          {/* Fluid Slider */}
          <div className="pt-2">
            <input
              id="parts-slider"
              type="range"
              min="2"
              max="50"
              value={parts}
              onChange={(e) => setParts(parseInt(e.target.value))}
              className="w-full h-2.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-500"
              aria-label="Number of split parts slider"
            />
            <div className="flex justify-between text-[11px] text-gray-500 font-mono mt-1">
              <span>Min: 2 Parts</span>
              <span>Max: 50 Parts</span>
            </div>
          </div>
        </div>

        {/* Quality Option Selector */}
        <div className="space-y-3">
          <label className="block text-xs sm:text-sm font-semibold text-gray-200 flex items-center space-x-2">
            <Settings2 className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Video Resolution Quality</span>
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
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
                className={`p-4 rounded-xl border text-left transition-all min-h-[64px] flex flex-col justify-center ${
                  quality === q.id
                    ? 'bg-rose-500/15 border-rose-500 text-white ring-1 ring-rose-500/50 shadow-lg shadow-rose-500/10'
                    : 'bg-slate-900/70 border-gray-800 text-gray-400 hover:border-gray-700 hover:text-gray-200'
                } focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none`}
              >
                <div className="text-xs sm:text-sm font-bold text-gray-200">{q.label}</div>
                <div className="text-[11px] text-gray-500 mt-0.5">{q.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Target Video Dimension / Aspect Ratio Module */}
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between">
            <label className="text-xs sm:text-sm font-semibold text-gray-200 flex items-center space-x-2">
              <Crop className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Target Aspect Ratio & Dimensions</span>
            </label>
            <span className="text-[11px] text-emerald-400 font-mono font-semibold">Shorts / Reels Ready</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {[
              { id: 'original', label: 'Native / Original', ratio: 'Source', desc: 'Unchanged aspect ratio', icon: Maximize2 },
              { id: '9:16', label: '9:16 Vertical Short', ratio: '1080x1920', desc: 'Shorts, TikTok, Reels', icon: Smartphone },
              { id: '16:9', label: '16:9 Widescreen', ratio: '1920x1080', desc: 'YouTube & Desktop TV', icon: Monitor },
              { id: '1:1', label: '1:1 Square', ratio: '1080x1080', desc: 'Instagram Feed Posts', icon: Square },
              { id: '4:5', label: '4:5 Portrait', ratio: '1080x1350', desc: 'Mobile Feed Portrait', icon: Smartphone },
            ].map((ar) => {
              const IconComp = ar.icon;
              const isSelected = aspectRatio === ar.id;
              return (
                <button
                  key={ar.id}
                  type="button"
                  onClick={() => setAspectRatio(ar.id as AspectRatioOption)}
                  className={`p-3.5 rounded-xl border text-left transition-all min-h-[76px] flex flex-col justify-between ${
                    isSelected
                      ? 'bg-emerald-500/15 border-emerald-500 text-white ring-1 ring-emerald-500/50 shadow-lg shadow-emerald-500/10'
                      : 'bg-slate-900/70 border-gray-800 text-gray-400 hover:border-gray-700 hover:text-gray-200'
                  } focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none`}
                >
                  <div className="flex items-center justify-between">
                    <IconComp className={`w-4 h-4 ${isSelected ? 'text-emerald-400' : 'text-gray-500'}`} />
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-950/80 border border-gray-800 text-gray-300">
                      {ar.ratio}
                    </span>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-200 mt-2">{ar.label}</div>
                    <div className="text-[10px] text-gray-500 truncate">{ar.desc}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Channel Branding Profile Selector */}
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between">
            <label htmlFor="channel-select" className="text-xs sm:text-sm font-semibold text-gray-200 flex items-center space-x-2">
              <Tv className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>Channel Profile Branding</span>
            </label>
            <span className="text-[11px] text-gray-400 font-mono">Auto Intro & Outro</span>
          </div>

          <div className="relative">
            <select
              id="channel-select"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full min-h-[48px] px-4 py-3 rounded-xl bg-slate-900 border border-gray-800 focus:border-rose-500 focus:ring-rose-500 text-white text-xs sm:text-sm font-semibold focus:outline-none focus:ring-2 transition-all cursor-pointer"
            >
              <option value="">None (Standard Split without Intros/Outros)</option>
              {channels.map((chan) => (
                <option key={chan.id} value={chan.id}>
                  ▼ {chan.display_name} (Auto Intro & Outro Branding)
                </option>
              ))}
            </select>
          </div>
          <p className="text-[11px] text-gray-400">
            Selecting a channel automatically prepends its intro video and appends its outro video to every split segment clip.
          </p>
        </div>

        {/* Touch-Friendly Full-Width Action Submit Button */}
        <button
          type="submit"
          disabled={isLoading || (urlTouched && !isUrlValid)}
          className="w-full min-h-[54px] py-4 rounded-xl sm:rounded-2xl bg-gradient-to-r from-rose-600 via-pink-600 to-rose-500 hover:from-rose-500 hover:to-pink-500 text-white font-heading font-bold text-sm sm:text-base md:text-lg shadow-xl shadow-rose-600/25 hover:shadow-rose-600/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 group focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Starting Video Pipeline...</span>
            </div>
          ) : (
            <>
              <span>Start Lossless Video Split</span>
              <Play className="w-4 h-4 sm:w-5 sm:h-5 fill-white transition-transform group-hover:translate-x-1 shrink-0" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
