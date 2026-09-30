export type PipelineStep = 'idle' | 'recording' | 'stt' | 'retrieval' | 'mrc' | 'tts' | 'playback';

export interface Passage {
  id?: string;
  text: string;
  score?: number;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'bot';
  text: string;
  audioUrl?: string;
  passage?: Passage;
}
