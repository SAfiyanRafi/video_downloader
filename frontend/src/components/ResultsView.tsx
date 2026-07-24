import React, { useState } from 'react';
import { Download, Archive, Clock, RefreshCw, Copy, Check, Folder } from 'lucide-react';
import type { JobDownloadsResponse } from '../types/job';
import { getAbsoluteDownloadUrl } from '../services/api';

interface ResultsViewProps {
  downloads: JobDownloadsResponse;
  onReset: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({ downloads, onReset }) => {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const formatSeconds = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = Math.floor(sec % 60);
    if (hrs > 0) {
      return `${hrs}h ${mins}m ${secs}s`;
    }
    return `${mins}m ${secs}s`;
  };

  const formatTimestamp = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = Math.floor(sec % 60);
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const copyToClipboard = (url: string, idx: number) => {
    const fullUrl = getAbsoluteDownloadUrl(url);
    navigator.clipboard.writeText(fullUrl);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const zipUrl = downloads.zip_url ? getAbsoluteDownloadUrl(downloads.zip_url) : null;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 px-0 sm:px-2">
      {/* Top Banner Hero Card */}
      <div className="glass-panel p-5 sm:p-8 rounded-2xl sm:rounded-3xl border border-emerald-500/30 bg-gradient-to-b from-emerald-500/10 via-slate-900 to-slate-900 space-y-6 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-mono text-xs font-semibold uppercase tracking-wider mb-2 border border-emerald-500/30">
              <Check className="w-3.5 h-3.5 shrink-0" />
              <span>Splitting Complete</span>
            </div>
            <h2 className="font-heading text-2xl sm:text-3xl md:text-4xl font-extrabold text-white">
              {downloads.clips.length} Video Clips Ready
            </h2>
            <p className="text-gray-300 text-xs sm:text-sm mt-1 leading-relaxed">
              Your video has been split losslessly into equal segments. Download individual MP4 clips or the complete ZIP archive.
            </p>
          </div>

          <button
            onClick={onReset}
            className="w-full sm:w-auto min-h-[44px] px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-gray-200 border border-gray-700 font-semibold text-xs sm:text-sm transition-all flex items-center justify-center space-x-2 shrink-0 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none"
          >
            <RefreshCw className="w-4 h-4 shrink-0" />
            <span>Split Another Video</span>
          </button>
        </div>

        {/* Hero ZIP Download Button (Touch-Friendly Minimum Height 54px) */}
        {zipUrl && (
          <a
            href={zipUrl}
            download="video_parts.zip"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full min-h-[54px] py-4 px-6 rounded-xl sm:rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 hover:from-emerald-500 hover:to-teal-500 text-white font-heading font-bold text-sm sm:text-base md:text-lg shadow-xl shadow-emerald-600/30 hover:shadow-emerald-600/40 transition-all flex items-center justify-center space-x-3 group focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
          >
            <Archive className="w-5 h-5 text-white transition-transform group-hover:scale-110 shrink-0" />
            <span>Download All Parts (.ZIP Archive)</span>
            <Download className="w-5 h-5 text-white ml-auto shrink-0 hidden sm:block" />
          </a>
        )}

        {/* Auto-Saved Folder Banner */}
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-3">
          <div className="flex items-center space-x-2 truncate">
            <Folder className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-semibold text-gray-200">Auto-Saved to Desktop:</span>
            <span className="font-mono text-[11px] text-amber-300 truncate">C:\Users\ABC\OneDrive\Desktop\Youtube\Download\Job_{downloads.job_id}</span>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 shrink-0">
            Exported
          </span>
        </div>

        {/* Video Specs Grid (2 cols on mobile, 4 cols on desktop) */}
        {downloads.metadata && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-gray-800">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Total Duration</p>
              <p className="text-white font-mono font-bold mt-0.5">{formatSeconds(downloads.metadata.duration)}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-gray-800">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Total Parts</p>
              <p className="text-rose-400 font-mono font-bold mt-0.5">{downloads.clips.length} Parts</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-gray-800">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Resolution</p>
              <p className="text-white font-mono font-bold mt-0.5 truncate">
                {downloads.metadata.width && downloads.metadata.height
                  ? `${downloads.metadata.width}x${downloads.metadata.height}`
                  : 'HD Standard'}
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-gray-800">
              <p className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">Codec Mode</p>
              <p className="text-emerald-400 font-mono font-bold mt-0.5 truncate">Stream Copy</p>
            </div>
          </div>
        )}
      </div>

      {/* Individual Clips Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1">
          <h3 className="font-heading text-xl sm:text-2xl font-extrabold text-white">
            Individual Video Clips
          </h3>
          <span className="text-xs text-gray-400 font-mono">
            {downloads.clips.length} Files Available
          </span>
        </div>

        {/* Responsive Grid: 1 col on mobile, 2 cols on tablet, 3 cols on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {downloads.clips.map((clip, idx) => {
            const downloadUrl = clip.download_url ? getAbsoluteDownloadUrl(clip.download_url) : '#';

            return (
              <div
                key={clip.part_number}
                className="p-5 rounded-2xl bg-slate-900/90 border border-gray-800 hover:border-gray-700 transition-all flex flex-col justify-between space-y-4 group hover:shadow-xl hover:shadow-slate-950/50"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-400 font-mono font-bold text-xs border border-rose-500/20">
                      Part {clip.part_number.toString().padStart(2, '0')}
                    </span>
                    <span className="text-gray-400 text-xs font-mono flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-gray-500 shrink-0" />
                      <span>{formatSeconds(clip.duration)}</span>
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/90 border border-gray-800/80 font-mono text-xs text-gray-300 flex items-center justify-between">
                    <span className="text-rose-400 font-bold">{formatTimestamp(clip.start_time)}</span>
                    <span className="text-gray-600 font-bold px-1">→</span>
                    <span className="text-rose-400 font-bold">{formatTimestamp(clip.end_time)}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 pt-2">
                  <a
                    href={downloadUrl}
                    download={`part_${clip.part_number.toString().padStart(3, '0')}.mp4`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 min-h-[44px] py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-rose-600 text-white font-semibold text-xs sm:text-sm transition-all flex items-center justify-center space-x-2 border border-gray-700 hover:border-rose-500 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none"
                  >
                    <Download className="w-4 h-4 shrink-0" />
                    <span>Download MP4</span>
                  </a>

                  <button
                    onClick={() => copyToClipboard(clip.download_url || '', idx)}
                    className="w-11 h-11 rounded-xl bg-slate-800 hover:bg-slate-700 border border-gray-700 text-gray-300 hover:text-white transition-all flex items-center justify-center shrink-0 focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:outline-none"
                    title="Copy direct download link"
                    aria-label="Copy direct download link"
                  >
                    {copiedIdx === idx ? (
                      <Check className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
