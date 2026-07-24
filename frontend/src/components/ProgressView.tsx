import React, { useEffect, useState } from 'react';
import { Download, Cpu, Scissors, Archive, CheckCircle2, Clock, Loader2, AlertCircle } from 'lucide-react';
import type { JobResponse, JobStatus } from '../types/job';

interface ProgressViewProps {
  job: JobResponse;
  onCancel?: () => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({ job }) => {
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
    <div className="w-full max-w-3xl mx-auto space-y-6">
      <div className="glass-panel-glow p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-mono font-semibold text-rose-400 uppercase tracking-widest">
              Job ID: #{job.job_id}
            </span>
            <h2 className="font-heading text-2xl font-bold text-white mt-0.5">
              Processing Video Pipeline
            </h2>
          </div>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-300 font-mono text-xs">
            <Clock className="w-3.5 h-3.5 text-rose-400" />
            <span>Elapsed: {formatTimer(secondsElapsed)}</span>
          </div>
        </div>

        {/* Video Metadata Card if available */}
        {job.metadata && (
          <div className="p-4 rounded-xl bg-slate-900/80 border border-gray-800/80 flex items-center justify-between text-xs">
            <div>
              <p className="text-gray-400 text-[11px] uppercase tracking-wider font-semibold">Video Title</p>
              <p className="text-white font-medium truncate max-w-md mt-0.5">{job.metadata.title || 'YouTube Video'}</p>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-[11px] uppercase tracking-wider font-semibold">Duration</p>
              <p className="text-rose-400 font-mono font-bold mt-0.5">{job.metadata.duration.toFixed(1)}s</p>
            </div>
          </div>
        )}

        {/* Animated Progress Bar */}
        <div>
          <div className="flex justify-between items-center text-xs font-semibold mb-2">
            <span className="text-gray-300 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 text-rose-400 animate-spin" />
              <span>{job.message}</span>
            </span>
            <span className="font-mono text-rose-400 font-extrabold text-sm">{job.progress.toFixed(0)}%</span>
          </div>

          <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-gray-800">
            <div
              className="h-full bg-gradient-to-r from-rose-600 via-pink-500 to-rose-400 rounded-full transition-all duration-500 shadow-lg shadow-rose-500/50"
              style={{ width: `${Math.max(job.progress, 5)}%` }}
            />
          </div>
        </div>

        {/* Stage Timeline Checklist */}
        <div className="space-y-3 pt-2">
          {stages.map((st) => {
            const state = getStageState(st.status);
            const Icon = st.icon;

            return (
              <div
                key={st.status}
                className={`p-3.5 rounded-xl border flex items-center justify-between transition-all ${
                  state === 'completed'
                    ? 'bg-slate-900/40 border-emerald-500/20 text-gray-300'
                    : state === 'active'
                    ? 'bg-rose-500/10 border-rose-500/40 text-white shadow-lg shadow-rose-500/10'
                    : 'bg-slate-900/20 border-gray-800/60 text-gray-500'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      state === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : state === 'active'
                        ? 'bg-rose-500 text-white animate-pulse'
                        : 'bg-slate-800 text-gray-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-semibold">{st.label}</span>
                </div>

                <div className="text-xs font-mono">
                  {state === 'completed' && (
                    <span className="text-emerald-400 font-medium flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Done</span>
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
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start space-x-3 text-red-400 text-xs">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Execution Error</p>
              <p className="text-red-300 mt-1">{job.error || 'An error occurred during video processing.'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
