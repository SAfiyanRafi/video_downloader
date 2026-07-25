import type { HookAnalysisRequest, HookAnalysisResponse } from '../types/hook';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1/hooks';

export async function analyzeHooks(req: HookAnalysisRequest): Promise<HookAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to analyze smart hooks');
  }

  return res.json();
}
