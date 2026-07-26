export type QualityOption = 'best' | '2160p' | '1440p' | '1080p' | '720p' | '480p' | 'audio_only';

export type AspectRatioOption = 'original' | '9:16' | '16:9' | '1:1' | '4:5';

export type ExportPreset = 'original_quality' | 'high_quality' | 'balanced' | 'small_file';

export type PaddingMode = 'black_bars' | 'blurred' | 'solid_color';

export type NamingTemplate = '{channel}_Part_{number}' | '{original}_Clip_{number}' | '{date}_{channel}_Part_{number}';

export type JobStatus =
  | 'pending'
  | 'downloading'
  | 'analyzing'
  | 'splitting'
  | 'zipping'
  | 'completed'
  | 'failed';

export interface ChannelProfile {
  id: string;
  display_name: string;
  intro?: string;
  outro?: string;
  filename_prefix?: string;
  resolution?: string;
  format?: string;
}

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
  parts?: number;
  url?: string;
}

export interface JobDownloadsResponse {
  job_id: string;
  status: JobStatus;
  zip_url?: string;
  clips: SegmentInfo[];
  metadata?: VideoMetadata;
}
