import React, { useEffect, useState } from 'react';
import { Download, Cpu, Scissors, Archive, CheckCircle2, Clock, Loader2, AlertCircle, XCircle } from 'lucide-react';
import type { JobResponse, JobStatus } from '../types/job';

interface ProgressViewProps {
  job: JobResponse;
  onCancel?: () => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({ job, onCancel }) => {
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const stages: { status: JobStatus; label: string; icon: React.FC<{ className?: string }> }[] = [
    { status: 'downloading', label: 'Downloading YouTube Video', icon: Download },
    { status: 'analyzing', label: 'Extracting Metadata (FFprobe)', icon: Cpu },
    { status: 'splitting', label: 'Lossless FFmpeg Splitting', icon: Scissors },
    { status: 'zipping', label: 'Packaging ZIP Archive', icon: Archive },
    { status: 'completed', label: 'Ready for Download', icon: CheckCircle2 },
  ];

  const getStageState = (stageStatus: JobStatus) => {
    const order: JobStatus[] = ['pending', 'downloading', 'analyzing', 'splitting', 'zipping', 'completed'];
    const currentIndex = order.indexOf(job.status);
    const stageIndex = order.indexOf(stageStatus);

    if (job.status === 'failed') return 'failed';
    if (currentIndex > stageIndex || job.status === 'completed') return 'completed';
    if (currentIndex === stageIndex) return 'active';
    return 'upcoming';
  };

  const formatTimer = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-0 sm:px-2 space-y-6">
      <div className="glass-panel-glow p-5 sm:p-8 rounded-2xl sm:rounded-3xl space-y-6">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <span className="text-[11px] font-mono font-semibold text-rose-400 uppercase tracking-widest px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/20">
              Job ID: #{job.job_id}
            </span>
            <h2 className="font-heading text-2xl sm:text-3xl font-extrabold text-white mt-2">
              Processing Video Pipeline
            </h2>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-end">
            <div className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-gray-800 text-gray-300 font-mono text-xs">
              <Clock className="w-4 h-4 text-rose-400 shrink-0" />
              <span>Elapsed: {formatTimer(secondsElapsed)}</span>
            </div>

            {onCancel && job.status === 'failed' && (
              <button
                type="button"
                onClick={onCancel}
                className="min-h-[40px] px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-semibold text-xs transition-all flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
              >
                <XCircle className="w-4 h-4 shrink-0" />
                <span>Back to Form</span>
              </button>
            )}

            {onCancel && job.status !== 'completed' && job.status !== 'failed' && (
              <button
                type="button"
                onClick={onCancel}
                className="min-h-[40px] px-3.5 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 hover:text-red-300 font-semibold text-xs transition-all flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:outline-none"
                title="Cancel ongoing video split job"
              >
                <XCircle className="w-4 h-4 shrink-0" />
                <span>Cancel Job</span>
              </button>
            )}
          </div>
        </div>

        {/* Video Metadata Card */}
        {job.metadata && (
          <div className="p-4 rounded-xl bg-slate-900/90 border border-gray-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <div className="min-w-0 flex-1">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Video Title</p>
              <p className="text-white font-medium truncate mt-0.5">{job.metadata.title || 'YouTube Video'}</p>
            </div>
            <div className="shrink-0 text-left sm:text-right">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Duration</p>
              <p className="text-rose-400 font-mono font-bold mt-0.5">{job.metadata.duration.toFixed(1)}s</p>
            </div>
          </div>
        )}

        {/* Fluid Responsive Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs font-semibold">
            <span className="text-gray-200 flex items-center space-x-2 truncate">
              <Loader2 className="w-4 h-4 text-rose-400 animate-spin shrink-0" />
              <span className="truncate">{job.message}</span>
            </span>
            <span className="font-mono text-rose-400 font-extrabold text-sm ml-2">{job.progress.toFixed(0)}%</span>
          </div>

          <div 
            className="w-full h-3.5 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-gray-800"
            role="progressbar"
            aria-valuenow={Math.round(job.progress)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Video split processing progress"
          >
            <div
              className="h-full bg-gradient-to-r from-rose-600 via-pink-500 to-rose-400 rounded-full transition-all duration-500 shadow-lg shadow-rose-500/50"
              style={{ width: `${Math.max(job.progress, 4)}%` }}
            />
          </div>
        </div>

        {/* Stage Timeline Checklist */}
        <div className="space-y-2.5 pt-2">
          {stages.map((st) => {
            const state = getStageState(st.status);
            const Icon = st.icon;

            return (
              <div
                key={st.status}
                className={`p-3.5 sm:p-4 rounded-xl border flex items-center justify-between transition-all ${
                  state === 'completed'
                    ? 'bg-slate-900/40 border-emerald-500/20 text-gray-300'
                    : state === 'active'
                    ? 'bg-rose-500/10 border-rose-500/40 text-white shadow-lg shadow-rose-500/10'
                    : 'bg-slate-900/20 border-gray-800/60 text-gray-500'
                }`}
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <div
                    className={`w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center shrink-0 ${
                      state === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : state === 'active'
                        ? 'bg-rose-500 text-white animate-pulse'
                        : 'bg-slate-800 text-gray-600'
                    }`}
                  >
                    <Icon className="w-4 h-4 sm:w-4.5 sm:h-4.5" />
                  </div>
                  <span className="text-xs sm:text-sm font-semibold truncate">{st.label}</span>
                </div>

                <div className="text-xs font-mono shrink-0 ml-2">
                  {state === 'completed' && (
                    <span className="text-emerald-400 font-medium flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                      <span className="hidden sm:inline">Done</span>
                    </span>
                  )}
                  {state === 'active' && (
                    <span className="text-rose-400 font-bold animate-pulse">In Progress...</span>
                  )}
                  {state === 'upcoming' && <span className="text-gray-600">Queued</span>}
                </div>
              </div>
            );
          })}
        </div>

        {job.status === 'failed' && (
          <div className="p-5 rounded-2xl bg-red-500/10 border border-red-500/30 space-y-4">
            <div className="flex items-start space-x-3 text-red-400">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-sm sm:text-base">Video Processing Failed</p>
                <p className="text-red-300 text-xs sm:text-sm mt-1 leading-relaxed">
                  {job.error || 'An error occurred during video processing.'}
                </p>
              </div>
            </div>

            {onCancel && (
              <div className="pt-1">
                <button
                  type="button"
                  onClick={onCancel}
                  className="w-full sm:w-auto min-h-[44px] px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-semibold text-xs sm:text-sm shadow-lg shadow-red-600/20 transition-all flex items-center justify-center space-x-2 focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
                >
                  <XCircle className="w-4 h-4 shrink-0" />
                  <span>Try Another Video URL</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
