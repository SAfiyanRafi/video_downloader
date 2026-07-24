import React, { useState } from 'react';
import { Sparkles, Copy, Check, FileText, Hash } from 'lucide-react';
import type { AIContentSuggestions } from '../../types/workflow';

interface AIUploadHelperProps {
  suggestions: AIContentSuggestions;
}

export const AIUploadHelper: React.FC<AIUploadHelperProps> = ({ suggestions }) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-purple-500/30 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
          <h4 className="text-xs sm:text-sm font-bold text-white">AI Upload Preparation Drafts</h4>
        </div>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
          Editable Suggestions
        </span>
      </div>

      {/* Title Candidates */}
      <div className="space-y-2">
        <div className="text-[11px] font-semibold text-gray-400">Suggested Video Titles</div>
        <div className="space-y-1.5">
          {suggestions.titles.map((t, idx) => (
            <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-gray-800 text-xs font-semibold text-gray-200">
              <span className="truncate pr-2">{t}</span>
              <button
                type="button"
                onClick={() => handleCopy(t, `title_${idx}`)}
                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-gray-300 text-[10px] flex items-center space-x-1 shrink-0"
              >
                {copiedKey === `title_${idx}` ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedKey === `title_${idx}` ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Description Draft & Hashtags */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div className="p-3 rounded-xl bg-slate-950 border border-gray-800 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-gray-400 flex items-center space-x-1">
              <FileText className="w-3.5 h-3.5 text-purple-400" />
              <span>Draft Description</span>
            </span>
            <button
              type="button"
              onClick={() => handleCopy(suggestions.description, 'desc')}
              className="text-[10px] text-purple-300 hover:underline flex items-center space-x-1"
            >
              {copiedKey === 'desc' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>Copy</span>
            </button>
          </div>
          <p className="text-[11px] text-gray-300 line-clamp-3 leading-relaxed">{suggestions.description}</p>
        </div>

        <div className="p-3 rounded-xl bg-slate-950 border border-gray-800 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-gray-400 flex items-center space-x-1">
              <Hash className="w-3.5 h-3.5 text-pink-400" />
              <span>Recommended Hashtags</span>
            </span>
            <button
              type="button"
              onClick={() => handleCopy(suggestions.hashtags.join(' '), 'hash')}
              className="text-[10px] text-pink-300 hover:underline flex items-center space-x-1"
            >
              {copiedKey === 'hash' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>Copy</span>
            </button>
          </div>
          <div className="flex flex-wrap gap-1">
            {suggestions.hashtags.map((h, i) => (
              <span key={i} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-pink-300 border border-gray-800">
                {h}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
