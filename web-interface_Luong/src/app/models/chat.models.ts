export type PipelineStep = 'idle' | 'recording' | 'stt' | 'retrieval' | 'mrc' | 'tts' | 'playback';

export interface Passage {
  id?: string;
  text: string;
  score?: number;
}

export type AnswerKind = 'qa' | 'multi' | 'compare' | 'yesno' | 'summary' | 'expand' | 'smalltalk' | 'math' | 'unknown';

export interface AskResponse {
  answer: string;
  kind: AnswerKind;
  intent?: string | null;
  session_id: string;
  resolved_question?: string | null;
  passage: Passage | null;
  parts: Array<{ question: string; answer: string; kind: AnswerKind }>;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'bot';
  text: string;
  audioUrl?: string;
  passage?: Passage;
  kind?: AnswerKind;
  /** Câu hỏi đã được hệ thống viết lại khi khác câu người dùng nói (vd. câu nối tiếp). */
  resolvedQuestion?: string;
}
