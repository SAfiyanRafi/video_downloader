import React from 'react';
import { History, X, Download, RotateCcw, Trash2, Clock, CheckCircle2, Film } from 'lucide-react';
import type { JobResponse } from '../types/job';

export interface HistoryItem {
  job: JobResponse;
  timestamp: string;
}

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryItem[];
  onSelectJob: (job: JobResponse) => void;
  onClearHistory: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectJob,
  onClearHistory,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/80 backdrop-blur-sm transition-opacity">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-gray-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-5 border-b border-gray-800 flex items-center justify-between bg-slate-900/90">
            <div className="flex items-center space-x-2 text-white font-heading font-bold text-lg">
              <History className="w-5 h-5 text-rose-500" />
              <span>Processing History</span>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-slate-800 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {history.length === 0 ? (
              <div className="text-center py-16 px-4 text-gray-400 space-y-3">
                <Film className="w-12 h-12 text-gray-600 mx-auto stroke-1" />
                <p className="font-semibold text-sm">No Recent Processing History</p>
                <p className="text-xs text-gray-500 max-w-xs mx-auto">
                  Completed split jobs and clips will automatically be saved here for quick access.
                </p>
              </div>
            ) : (
              history.map((item, idx) => {
                const { job, timestamp } = item;
                return (
                  <div
                    key={job.job_id || idx}
                    className="p-4 rounded-2xl bg-slate-950/60 border border-gray-800/80 hover:border-gray-700 transition-all space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                          <span className="text-xs font-mono font-bold text-gray-200">#{job.job_id}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold uppercase">
                            {job.parts} Parts
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 truncate max-w-[240px] mt-1 font-mono">{job.url}</p>
                      </div>
                      <div className="text-[10px] text-gray-500 flex items-center space-x-1 font-mono">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Quick Action Buttons */}
                    <div className="flex items-center gap-2 pt-1 border-t border-gray-800/50">
                      <button
                        onClick={() => {
                          onSelectJob(job);
                          onClose();
                        }}
                        className="flex-1 min-h-[36px] py-1.5 px-3 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white font-semibold text-xs transition-all flex items-center justify-center space-x-1.5 shadow-md shadow-rose-600/20"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>View Clips</span>
                      </button>

                      <button
                        onClick={() => {
                          onSelectJob(job);
                          onClose();
                        }}
                        className="px-3 min-h-[36px] py-1.5 rounded-xl bg-slate-900 border border-gray-800 hover:border-gray-700 text-gray-300 text-xs font-medium transition-all flex items-center space-x-1"
                        title="Reprocess Video"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Reprocess</span>
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer Actions */}
          {history.length > 0 && (
            <div className="p-4 border-t border-gray-800 bg-slate-900/90 flex justify-between items-center">
              <span className="text-xs text-gray-400 font-mono">{history.length} Total Saved Jobs</span>
              <button
                onClick={onClearHistory}
                className="text-xs text-red-400 hover:text-red-300 flex items-center space-x-1 px-2.5 py-1.5 rounded-lg hover:bg-red-500/10 transition-all font-semibold"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear History</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
