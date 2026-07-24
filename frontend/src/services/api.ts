import type { JobResponse, JobDownloadsResponse, QualityOption, AspectRatioOption } from '../types/job';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';

export async function createSplitJob(
  url: string,
  parts: number = 4,
  quality: QualityOption = 'best',
  aspectRatio: AspectRatioOption = 'original',
  channel?: string
): Promise<JobResponse> {
  try {
    const payload: any = { url, parts, quality, aspect_ratio: aspectRatio };
    if (channel) {
      payload.channel = channel;
    }

    const response = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to submit YouTube video for splitting');
    }

    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message === 'Failed to fetch') {
      throw new Error('Backend server disconnected. Please verify Uvicorn server is running on http://localhost:8000.');
    }
    throw err;
  }
}

export async function fetchChannels(): Promise<import('../types/job').ChannelProfile[]> {
  try {
    const response = await fetch(`${API_BASE}/channels`);
    if (!response.ok) {
      return [];
    }
    return response.json();
  } catch (err) {
    console.warn('Failed to fetch channels from backend:', err);
    return [];
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
    if (response.status === 404) {
      return { job_id: jobId, status: 'failed', progress: 0, message: 'Job cleared', created_at: '', updated_at: '' };
    }
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
