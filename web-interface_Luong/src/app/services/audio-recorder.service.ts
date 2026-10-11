import { Injectable } from '@angular/core';
import { toWav16k } from '../utils/wav';

@Injectable({ providedIn: 'root' })
export class AudioRecorderService {
  private recorder?: MediaRecorder;
  private chunks: Blob[] = [];

  async start(): Promise<void> {
    if (!globalThis.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('Micro chỉ hoạt động trên HTTPS hoặc localhost.');
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.chunks = [];
    this.recorder = new MediaRecorder(stream);
    this.recorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };
    this.recorder.start();
  }

  /** Stop recording and return the audio as a 16 kHz mono WAV blob. */
  stop(): Promise<Blob> {
    const recorder = this.recorder;
    if (!recorder) return Promise.reject(new Error('Chưa bắt đầu thu âm.'));

    return new Promise<Blob>((resolve, reject) => {
      recorder.onstop = () => {
        recorder.stream.getTracks().forEach((t) => t.stop());
        this.recorder = undefined;
        const raw = new Blob(this.chunks, { type: recorder.mimeType });
        toWav16k(raw).then(resolve, reject);
      };
      recorder.stop();
    });
  }
}
