import type { JobResponse, JobDownloadsResponse, QualityOption } from '../types/job';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';

export async function createSplitJob(url: string, parts: number, quality: QualityOption): Promise<JobResponse> {
  try {
    const response = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, parts, quality }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: 'Failed to create job' }));
      throw new Error(errData.detail || 'Failed to submit YouTube video for splitting');
    }

    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message === 'Failed to fetch') {
      throw new Error('Cannot connect to backend API server. Please start the backend server on http://localhost:8000');
    }
    throw err;
  }
}

export async function fetchJobStatus(jobId: string): Promise<JobResponse> {
  try {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch status for job ${jobId}`);
    }
    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message === 'Failed to fetch') {
      throw new Error('Backend server disconnected');
    }
    throw err;
  }
}

export async function cancelSplitJob(jobId: string): Promise<JobResponse> {
  try {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to cancel job ${jobId}`);
    }
    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message === 'Failed to fetch') {
      throw new Error('Backend server disconnected');
    }
    throw err;
  }
}

export async function fetchJobDownloads(jobId: string): Promise<JobDownloadsResponse> {
  try {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/downloads`);
    if (!response.ok) {
      throw new Error(`Failed to fetch downloads for job ${jobId}`);
    }
    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message === 'Failed to fetch') {
      throw new Error('Backend server disconnected');
    }
    throw err;
  }
}

export function getAbsoluteDownloadUrl(relativeOrAbsoluteUrl: string): string {
  if (relativeOrAbsoluteUrl.startsWith('http')) {
    return relativeOrAbsoluteUrl;
  }
  const baseHost = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  return `${baseHost}${relativeOrAbsoluteUrl}`;
}
