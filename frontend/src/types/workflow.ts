export interface WorkflowProfile {
  id: string;
  display_name: string;
  description: string;
  aspect_ratio: string;
  padding_mode: string;
  allow_intro_outro: boolean;
  enable_subtitles: boolean;
  subtitle_preset: string;
  enable_thumbnails: boolean;
  export_preset: string;
}

export interface AIContentSuggestions {
  titles: string[];
  description: string;
  hashtags: string[];
  chapters: string[];
}
