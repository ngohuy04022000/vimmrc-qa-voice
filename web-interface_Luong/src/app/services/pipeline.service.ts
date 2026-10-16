import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Passage } from '../models/chat.models';

@Injectable({ providedIn: 'root' })
export class PipelineService {
  private readonly http = inject(HttpClient);

  transcribe(audio: Blob): Observable<string> {
    const form = new FormData();
    form.append('file', audio, 'question.wav');
    return this.http.post<{ text: string }>('/api/stt', form).pipe(map((r) => r.text.trim()));
  }

  retrieve(question: string, topK = 3): Observable<Passage[]> {
    return this.http
      .post<{ passages: Passage[] }>('/api/retrieve', { question, top_k: topK })
      .pipe(map((r) => r.passages ?? []));
  }

  answerQuestion(passage: string, question: string): Observable<string> {
    return this.http
      .post<{ answer: string }>('/api/answer', { passage, question })
      .pipe(map((r) => r.answer.trim()));
  }

  synthesize(text: string): Observable<Blob> {
    return this.http.post('/api/tts', { text }, { responseType: 'blob' });
  }
}
