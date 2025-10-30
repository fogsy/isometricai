export type FrameScore = {
  index: number;
  timestamp: number;
  score: number;
};

export type DetectionResult = {
  id: number;
  media_type: 'image' | 'video';
  score: number;
  threshold: number;
  label: 'synthetic' | 'real';
  model_name: string;
  model_version: string;
  created_at: string;
  metadata?: Record<string, unknown> | null;
  frames?: FrameScore[];
};
