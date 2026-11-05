export type PipelineStep = 'idle' | 'recording' | 'stt' | 'retrieval' | 'mrc' | 'tts' | 'playback';

export interface Passage {
  id?: string;
  text: string;
  score?: number;
}

export interface AskResponse {
  answer: string;
  kind: string;
  intent?: string | null;
  session_id: string;
  resolved_question?: string | null;
  passage?: Passage | null;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'bot';
  text: string;
  audioUrl?: string;
  passage?: Passage;
  time?: string;
  source?: 'voice' | 'text';
}
