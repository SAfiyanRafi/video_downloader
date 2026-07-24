import type { StudioJobRequest, StudioJobResponse } from '../types/studio';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1/studio';

export async function createStudioJob(req: StudioJobRequest): Promise<StudioJobResponse> {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start Creator Studio job');
  }
  return res.json();
}

export async function fetchStudioJobStatus(jobId: string): Promise<StudioJobResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch status for studio job ${jobId}`);
  }
  return res.json();
}

export async function scanWatchFolder(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/watch-folder`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}
