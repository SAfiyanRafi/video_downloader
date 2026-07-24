export type SubtitleStylePreset = 'tiktok' | 'mrbeast' | 'gaming' | 'podcast' | 'minimal';
export type SubtitleMode = 'burned_in' | 'soft_srt' | 'both';

export interface StudioJobRequest {
  video_path: string;
  enable_subtitles: boolean;
  subtitle_preset: SubtitleStylePreset;
  subtitle_mode: SubtitleMode;
  normalize_audio: boolean;
  target_lufs: number;
  pitch_semitones: number;
  whisper_model: string;
}

export interface StudioJobResponse {
  job_id: string;
  video_name: string;
  status: string;
  progress: number;
  message: string;
  output_video_path: string | null;
  srt_path: string | null;
  created_at: string;
  updated_at: string;
  error: string | null;
}
