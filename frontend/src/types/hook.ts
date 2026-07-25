export type HookSensitivity = 'low' | 'medium' | 'high';

export interface HookCandidate {
  id: string;
  timestamp: number;
  timestamp_formatted: string;
  confidence: number;
  reasons: string[];
  text_snippet?: string;
  speech_energy: number;
  has_scene_change: boolean;
  has_curiosity_phrase: boolean;
}

export interface HookAnalysisRequest {
  video_path: string;
  sensitivity: HookSensitivity;
  max_suggestions: number;
  min_confidence: number;
  search_duration_seconds?: number;
}

export interface HookAnalysisResponse {
  video_name: string;
  total_scene_changes: number;
  candidates: HookCandidate[];
  processing_time_seconds: number;
}
