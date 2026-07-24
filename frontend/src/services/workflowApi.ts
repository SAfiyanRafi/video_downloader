import type { WorkflowProfile, AIContentSuggestions } from '../types/workflow';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1/workflows';

export async function fetchWorkflows(): Promise<WorkflowProfile[]> {
  try {
    const res = await fetch(`${API_BASE}`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function fetchAISuggestions(title: string, transcript: string = ''): Promise<AIContentSuggestions | null> {
  try {
    const res = await fetch(`${API_BASE}/ai-suggestions?title=${encodeURIComponent(title)}&transcript=${encodeURIComponent(transcript)}`, {
      method: 'POST'
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
