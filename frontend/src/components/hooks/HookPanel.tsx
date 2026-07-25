import React, { useState } from 'react';
import { Sparkles, Check, AlertCircle, Zap } from 'lucide-react';
import type { HookCandidate, HookAnalysisResponse, HookSensitivity } from '../../types/hook';
import { analyzeHooks } from '../../services/hookApi';

interface HookPanelProps {
  videoPath: string;
  onSelectHook: (candidate: HookCandidate) => void;
}

export const HookPanel: React.FC<HookPanelProps> = ({ videoPath, onSelectHook }) => {
  const [sensitivity, setSensitivity] = useState<HookSensitivity>('medium');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<HookAnalysisResponse | null>(null);
  const [selectedHookId, setSelectedHookId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    if (!videoPath) {
      setError('Please select a video file first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    try {
      const res = await analyzeHooks({
        video_path: videoPath,
        sensitivity,
        max_suggestions: 5,
        min_confidence: sensitivity === 'high' ? 50.0 : sensitivity === 'medium' ? 65.0 : 75.0,
        search_duration_seconds: 300.0
      });
      setAnalysis(res);
    } catch (err: any) {
      setError(err.message || 'Failed to run hook detection');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 bg-slate-900/90 space-y-4">
      {/* Panel Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Zap className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <h3 className="text-xs sm:text-sm font-extrabold text-white">Smart Hook Detection Engine</h3>
            <p className="text-[11px] text-gray-400">AI Editorial Advisor for Short-Form Content Starting Points</p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleRunAnalysis}
          disabled={isAnalyzing || !videoPath}
          className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-extrabold text-xs transition-all shadow-md shadow-amber-500/20 disabled:opacity-50 flex items-center space-x-1.5 shrink-0"
        >
          {isAnalyzing ? (
            <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
          ) : (
            <Sparkles className="w-3.5 h-3.5" />
          )}
          <span>{isAnalyzing ? 'Analyzing Hooks...' : 'Detect Hooks'}</span>
        </button>
      </div>

      {/* Sensitivity Settings */}
      <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-gray-800 text-xs">
        <span className="text-gray-400 font-semibold">Detection Sensitivity</span>
        <div className="flex items-center space-x-1.5">
          {(['low', 'medium', 'high'] as HookSensitivity[]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSensitivity(s)}
              className={`px-2.5 py-1 rounded-lg text-[10px] uppercase font-mono font-bold transition-all ${
                sensitivity === s
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-slate-900 text-gray-400 hover:text-white'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Analysis Results Candidate List */}
      {analysis && (
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between text-[11px] text-gray-400">
            <span>Found {analysis.candidates.length} Hook Candidates ({analysis.total_scene_changes} Scene Cuts)</span>
            <span className="font-mono text-amber-400 font-bold">Processed in {analysis.processing_time_seconds}s</span>
          </div>

          <div className="space-y-2.5">
            {analysis.candidates.map((cand) => {
              const isSelected = selectedHookId === cand.id;
              return (
                <div
                  key={cand.id}
                  className={`p-3.5 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-amber-500/15 border-amber-500 text-white ring-1 ring-amber-500/50'
                      : 'bg-slate-950 border-gray-800 text-gray-300 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-extrabold text-xs px-2 py-0.5 rounded bg-slate-900 border border-gray-800 text-amber-300">
                        ⏱️ {cand.timestamp_formatted} ({cand.timestamp}s)
                      </span>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                        {cand.confidence}% Confidence
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedHookId(cand.id);
                          onSelectHook(cand);
                        }}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                          isSelected
                            ? 'bg-emerald-500 text-slate-950 shadow-md'
                            : 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30'
                        }`}
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>{isSelected ? 'Hook Selected' : 'Select Hook'}</span>
                      </button>
                    </div>
                  </div>

                  {cand.text_snippet && (
                    <p className="text-xs text-gray-200 font-medium italic mb-2">"{cand.text_snippet}"</p>
                  )}

                  <div className="flex flex-wrap gap-1.5">
                    {cand.reasons.map((r, i) => (
                      <span key={i} className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-900 text-gray-300 border border-gray-800">
                        {r}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
