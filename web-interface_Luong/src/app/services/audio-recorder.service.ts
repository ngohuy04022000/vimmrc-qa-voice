import { Injectable } from '@angular/core';
import { AutoStopReason, SilenceDetector } from '../utils/silence-detector';
import { toWav16k } from '../utils/wav';

const POLL_MS = 80;

@Injectable({ providedIn: 'root' })
export class AudioRecorderService {
  private recorder?: MediaRecorder;
  private chunks: Blob[] = [];
  private ctx?: AudioContext;
  private timer?: ReturnType<typeof setInterval>;

  /** onAutoStop được gọi (một lần) khi người dùng ngừng nói, không nói gì, hoặc quá dài. */
  async start(onAutoStop?: (reason: AutoStopReason) => void): Promise<void> {
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
    if (onAutoStop) this.watchSilence(stream, onAutoStop);
  }

  private watchSilence(stream: MediaStream, onAutoStop: (reason: AutoStopReason) => void): void {
    const ctx = new AudioContext();
    void ctx.resume();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 1024;
    ctx.createMediaStreamSource(stream).connect(analyser);
    const buf = new Float32Array(analyser.fftSize);
    const detector = new SilenceDetector();
    this.ctx = ctx;
    this.timer = setInterval(() => {
      analyser.getFloatTimeDomainData(buf);
      let sum = 0;
      for (const v of buf) sum += v * v;
      const reason = detector.push(Math.sqrt(sum / buf.length), performance.now());
      if (reason) {
        this.stopWatching();
        onAutoStop(reason);
      }
    }, POLL_MS);
  }

  private stopWatching(): void {
    if (this.timer !== undefined) clearInterval(this.timer);
    this.timer = undefined;
    void this.ctx?.close();
    this.ctx = undefined;
  }

  /** Huỷ phiên thu, bỏ âm thanh (dùng khi không nghe thấy gì). */
  cancel(): void {
    this.stopWatching();
    const recorder = this.recorder;
    this.recorder = undefined;
    if (!recorder) return;
    recorder.ondataavailable = null;
    recorder.onstop = () => recorder.stream.getTracks().forEach((t) => t.stop());
    if (recorder.state !== 'inactive') recorder.stop();
    else recorder.stream.getTracks().forEach((t) => t.stop());
  }

  /** Stop recording and return the audio as a 16 kHz mono WAV blob. */
  stop(): Promise<Blob> {
    this.stopWatching();
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
