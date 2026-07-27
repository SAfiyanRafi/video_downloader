import React, { useState, useEffect } from 'react';
import {
  Sparkles, CheckCircle2, AlertCircle, Folder, RefreshCw, Volume2, Type, Video, Film
} from 'lucide-react';
import type { SubtitleStylePreset, SubtitleMode, StudioJobResponse } from '../../types/studio';
import { createStudioJob, fetchStudioJobStatus, scanWatchFolder } from '../../services/studioApi';
import { AIUploadHelper } from './AIUploadHelper';
import { HookPanel } from '../hooks/HookPanel';

export const StudioDashboard: React.FC = () => {
  const [detectedVideos, setDetectedVideos] = useState<string[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string>('');
  const [enableSubtitles, setEnableSubtitles] = useState(true);
  const [subtitlePreset, setSubtitlePreset] = useState<SubtitleStylePreset>('tiktok');
  const [subtitleMode, setSubtitleMode] = useState<SubtitleMode>('burned_in');
  const [normalizeAudio, setNormalizeAudio] = useState(true);
  const [targetLufs, setTargetLufs] = useState<number>(-16.0);
  const [pitchSemitones, setPitchSemitones] = useState<number>(0.0);
  const [whisperModel, setWhisperModel] = useState<string>('tiny');
  
  const [activeJob, setActiveJob] = useState<StudioJobResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWatchFolder = async () => {
    const videos = await scanWatchFolder();
    setDetectedVideos(videos);
    if (videos.length > 0 && !selectedVideo) {
      setSelectedVideo(videos[0]);
    }
  };

  useEffect(() => {
    loadWatchFolder();
  }, []);

  // Poll active studio job status
  useEffect(() => {
    if (!activeJob || activeJob.status === 'COMPLETED' || activeJob.status === 'FAILED') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await fetchStudioJobStatus(activeJob.job_id);
        setActiveJob(updated);
      } catch (e) {
        console.error('Failed to poll studio job status:', e);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeJob]);

  const handleStartProcessing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedVideo) {
      setError('Please select or specify a local video path');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const job = await createStudioJob({
        video_path: selectedVideo,
        enable_subtitles: enableSubtitles,
        subtitle_preset: subtitlePreset,
        subtitle_mode: subtitleMode,
        normalize_audio: normalizeAudio,
        target_lufs: targetLufs,
        pitch_semitones: pitchSemitones,
        whisper_model: whisperModel
      });
      setActiveJob(job);
    } catch (err: any) {
      setError(err.message || 'Failed to start Creator Studio processing');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 px-2 sm:px-4 py-4">
      {/* Studio Header Hero Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-purple-500/30 bg-gradient-to-b from-purple-500/10 via-slate-900 to-slate-900 space-y-4 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-mono text-xs font-semibold uppercase tracking-wider mb-2 border border-purple-500/30">
              <Sparkles className="w-3.5 h-3.5 shrink-0" />
              <span>Creator Studio Platform</span>
            </div>
            <h1 className="font-heading text-2xl sm:text-4xl font-extrabold text-white">
              AI Subtitles & Audio Post-Processing
            </h1>
            <p className="text-gray-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Transform raw split videos into upload-ready social media content with Whisper AI subtitles, stylized typography burn-in, and EBU R128 audio loudness normalization.
            </p>
          </div>

          <button
            onClick={loadWatchFolder}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-gray-200 border border-gray-700 font-semibold text-xs sm:text-sm transition-all flex items-center space-x-2 shrink-0"
          >
            <RefreshCw className="w-4 h-4 shrink-0" />
            <span>Scan Folder</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Controls Sidebar (7 Cols) */}
        <form onSubmit={handleStartProcessing} className="lg:col-span-7 space-y-6">
          {/* Detected Video Selection */}
          <div className="glass-panel p-5 rounded-2xl border border-gray-800 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs sm:text-sm font-bold text-gray-200 flex items-center space-x-2">
                <Folder className="w-4 h-4 text-amber-400" />
                <span>Select Input Video File</span>
              </label>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold">
                {detectedVideos.length} Videos Found
              </span>
            </div>

            {detectedVideos.length > 0 ? (
              <select
                value={selectedVideo}
                onChange={(e) => setSelectedVideo(e.target.value)}
                className="w-full px-3.5 py-3 rounded-xl bg-slate-950 border border-gray-800 text-white text-xs font-mono focus:ring-2 focus:ring-purple-500 focus:outline-none"
              >
                {detectedVideos.map((path, idx) => (
                  <option key={idx} value={path}>
                    🎥 {path.split('\\').pop() || path}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={selectedVideo}
                onChange={(e) => setSelectedVideo(e.target.value)}
                placeholder="Enter absolute path to video file (e.g. C:\Users\...\video.mp4)"
                className="w-full px-3.5 py-3 rounded-xl bg-slate-950 border border-gray-800 text-white text-xs font-mono focus:ring-2 focus:ring-purple-500 focus:outline-none"
              />
            )}

            {/* Smart Hook Detection Engine Panel */}
            {selectedVideo && (
              <HookPanel
                videoPath={selectedVideo}
                onSelectHook={(cand) => {
                  console.log('Selected hook candidate:', cand);
                }}
              />
            )}
          </div>

          {/* Subtitle Engine Options */}
          <div className="glass-panel p-5 rounded-2xl border border-gray-800 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs sm:text-sm font-bold text-gray-200 flex items-center space-x-2">
                <Type className="w-4 h-4 text-purple-400" />
                <span>AI Subtitle Engine & Typography</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer text-xs text-purple-300">
                <input
                  type="checkbox"
                  checked={enableSubtitles}
                  onChange={(e) => setEnableSubtitles(e.target.checked)}
                  className="w-4 h-4 rounded accent-purple-500 bg-slate-950 border-gray-700"
                />
                <span>Enable Subtitles</span>
              </label>
            </div>

            {enableSubtitles && (
              <div className="space-y-4 pt-1">
                {/* Style Presets */}
                <div>
                  <div className="text-xs text-gray-400 mb-2 font-semibold">Select Subtitle Style Preset</div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                    {[
                      { id: 'tiktok', label: '🔥 TikTok', desc: 'Vivid Yellow & Black Outline' },
                      { id: 'mrbeast', label: '⚡ MrBeast', desc: 'High Impact Centered Pop' },
                      { id: 'gaming', label: '🎮 Gaming', desc: 'Neon Cyan & Bold Stroke' },
                      { id: 'podcast', label: '🎙️ Podcast', desc: 'Clean White Translucent Box' },
                      { id: 'minimal', label: '✨ Minimal', desc: 'Soft Drop Shadow' },
                    ].map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSubtitlePreset(p.id as SubtitleStylePreset)}
                        className={`p-3 rounded-xl border text-left transition-all ${
                          subtitlePreset === p.id
                            ? 'bg-purple-500/20 border-purple-500 text-white font-bold ring-1 ring-purple-500'
                            : 'bg-slate-950 border-gray-800 text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        <div className="text-xs">{p.label}</div>
                        <div className="text-[10px] text-gray-500 mt-0.5">{p.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Subtitle Export Mode */}
                <div className="grid grid-cols-2 gap-3 pt-1">
                  <div>
                    <label className="text-[11px] font-semibold text-gray-400 block mb-1">Burn-in Mode</label>
                    <select
                      value={subtitleMode}
                      onChange={(e) => setSubtitleMode(e.target.value as SubtitleMode)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-gray-800 text-white text-xs font-semibold focus:outline-none"
                    >
                      <option value="burned_in">🔥 Burn-in Video Captions</option>
                      <option value="soft_srt">📄 Export Separate .SRT File</option>
                      <option value="both">✨ Both (Burned + .SRT)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-gray-400 block mb-1">Whisper AI Model</label>
                    <select
                      value={whisperModel}
                      onChange={(e) => setWhisperModel(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-gray-800 text-white text-xs font-semibold focus:outline-none"
                    >
                      <option value="tiny">⚡ Tiny (Fastest)</option>
                      <option value="base">✨ Base (Balanced)</option>
                      <option value="small">🎯 Small (Higher Accuracy)</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Audio Post-Processing Options */}
          <div className="glass-panel p-5 rounded-2xl border border-gray-800 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs sm:text-sm font-bold text-gray-200 flex items-center space-x-2">
                <Volume2 className="w-4 h-4 text-emerald-400" />
                <span>Audio Loudness & Pitch Control</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer text-xs text-emerald-300">
                <input
                  type="checkbox"
                  checked={normalizeAudio}
                  onChange={(e) => setNormalizeAudio(e.target.checked)}
                  className="w-4 h-4 rounded accent-emerald-500 bg-slate-950 border-gray-700"
                />
                <span>EBU R128 Normalization</span>
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-[11px] font-semibold text-gray-400 block mb-1">
                  Target Loudness ({targetLufs} LUFS)
                </label>
                <select
                  value={targetLufs}
                  onChange={(e) => setTargetLufs(parseFloat(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-gray-800 text-white text-xs font-semibold focus:outline-none"
                >
                  <option value={-16.0}>📱 -16 LUFS (TikTok, Shorts, Reels)</option>
                  <option value={-24.0}>📺 -24 LUFS (Standard TV & Desktop)</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-gray-400 block mb-1">
                  Pitch Adjustment ({pitchSemitones > 0 ? `+${pitchSemitones}` : pitchSemitones} semitones)
                </label>
                <input
                  type="range"
                  min="-3.0"
                  max="3.0"
                  step="0.5"
                  value={pitchSemitones}
                  onChange={(e) => setPitchSemitones(parseFloat(e.target.value))}
                  className="w-full accent-emerald-500 bg-slate-950 h-2 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Action Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting || !selectedVideo}
            className="w-full min-h-[52px] py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 via-pink-600 to-purple-500 hover:from-purple-500 hover:to-pink-500 text-white font-heading font-bold text-base shadow-xl shadow-purple-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isSubmitting ? (
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Starting Studio Pipeline...</span>
              </div>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Enhance Video in Creator Studio</span>
              </>
            )}
          </button>
        </form>

        {/* Live Processing Output & Queue (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-gray-800 space-y-4">
            <h3 className="font-heading text-lg font-bold text-white flex items-center space-x-2">
              <Film className="w-5 h-5 text-purple-400" />
              <span>Studio Processing Queue</span>
            </h3>

            {activeJob ? (
              <div className="space-y-4 p-4 rounded-2xl bg-slate-950/80 border border-gray-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white truncate max-w-[200px]">{activeJob.video_name}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    activeJob.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-300' :
                    activeJob.status === 'FAILED' ? 'bg-rose-500/20 text-rose-300' : 'bg-purple-500/20 text-purple-300'
                  }`}>
                    {activeJob.status}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-gray-400">
                    <span>{activeJob.message}</span>
                    <span className="font-mono">{activeJob.progress}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                      style={{ width: `${activeJob.progress}%` }}
                    />
                  </div>
                </div>

                {/* Completed Output */}
                {activeJob.status === 'COMPLETED' && activeJob.output_video_path && (
                  <div className="pt-2 space-y-4">
                    <div className="text-xs text-emerald-400 font-semibold flex items-center space-x-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Upload Ready Video Generated</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900 border border-gray-800 text-[11px] font-mono text-gray-300 break-all space-y-2">
                      <div>Saved to: {activeJob.output_video_path}</div>
                      <div className="flex flex-wrap gap-2 pt-1">
                        <a
                          href={`http://localhost:8000/api/v1/studio/jobs/${activeJob.job_id}/download/video`}
                          download
                          className="px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center space-x-1.5 transition-all shadow-md"
                        >
                          <Film className="w-3.5 h-3.5" />
                          <span>Download Enhanced Video MP4</span>
                        </a>
                        {activeJob.srt_path && (
                          <a
                            href={`http://localhost:8000/api/v1/studio/jobs/${activeJob.job_id}/download/srt`}
                            download
                            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-200 font-semibold text-xs flex items-center space-x-1.5 transition-all border border-gray-700"
                          >
                            <Type className="w-3.5 h-3.5 text-pink-400" />
                            <span>Download SRT Subtitles</span>
                          </a>
                        )}
                      </div>
                    </div>

                    <AIUploadHelper
                      suggestions={{
                        titles: [
                          `🔥 ${activeJob.video_name.replace(/_/g, ' ')} — Must Watch!`,
                          `What Happens In ${activeJob.video_name.replace(/_/g, ' ')}?`,
                          `The Ultimate Guide to ${activeJob.video_name.replace(/_/g, ' ')} 🚀`
                        ],
                        description: `Enjoy this video clip from ${activeJob.video_name}!\n\n📌 Subscribe for more high-quality clips & shorts updates.\nLIKE, SHARE & COMMENT below your favorite moments!`,
                        hashtags: ['#Shorts', '#Viral', '#Trending', '#YouTube', '#Reels', '#TikTok'],
                        chapters: ['00:00 - Introduction & Key Hook', '00:30 - Main Highlights', '01:30 - Conclusion']
                      }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500 text-xs rounded-2xl bg-slate-950/40 border border-dashed border-gray-800 space-y-2">
                <Video className="w-8 h-8 mx-auto text-gray-600" />
                <p>No active studio job. Select a video and click Enhance Video to start processing.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
