export type QualityOption = 'best' | '1080p' | '720p' | 'audio_only';

export type JobStatus =
  | 'pending'
  | 'downloading'
  | 'analyzing'
  | 'splitting'
  | 'zipping'
  | 'completed'
  | 'failed';

export interface VideoMetadata {
  duration: number;
  width?: number;
  height?: number;
  fps?: number;
  codec_name?: string;
  audio_codec?: string;
  bit_rate?: number;
  file_size?: number;
  title?: string;
}

export interface SegmentInfo {
  part_number: number;
  start_time: number;
  end_time: number;
  duration: number;
  filename: string;
  download_url?: string;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
  error?: string;
  metadata?: VideoMetadata;
}

export interface JobDownloadsResponse {
  job_id: string;
  status: JobStatus;
  zip_url?: string;
  clips: SegmentInfo[];
  metadata?: VideoMetadata;
}
