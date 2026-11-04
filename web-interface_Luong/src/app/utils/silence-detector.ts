export type AutoStopReason = 'silence' | 'no-speech' | 'max-duration';

export interface SilenceOptions {
  /** Im lặng liên tục sau khi đã nói thì coi là hết câu. */
  silenceMs: number;
  /** Phải có ít nhất chừng này giọng nói mới tính là đã nói (tránh tiếng click, tiếng thở). */
  minSpeechMs: number;
  /** Không nghe thấy gì sau chừng này thì bỏ cuộc. */
  noSpeechMs: number;
  maxMs: number;
  /** Thời gian đo tiếng ồn nền ở đầu phiên để đặt ngưỡng. */
  calibrateMs: number;
}

export const DEFAULT_SILENCE_OPTIONS: SilenceOptions = {
  silenceMs: 1300,
  minSpeechMs: 250,
  noSpeechMs: 8000,
  maxMs: 30000,
  calibrateMs: 400,
};

const MIN_THRESHOLD = 0.02;
const MAX_THRESHOLD = 0.06;

/**
 * Nhận từng mẫu mức âm lượng (RMS 0..1) kèm thời điểm; trả về lý do dừng khi đủ điều kiện.
 * Ngưỡng = 3 × tiếng ồn nền đo ở calibrateMs đầu, kẹp trong [0,02; 0,06].
 */
export class SilenceDetector {
  private startMs?: number;
  private lastMs = 0;
  private noiseSum = 0;
  private noiseCount = 0;
  private threshold = MIN_THRESHOLD;
  private speechMs = 0;
  private silenceMs = 0;
  private spoke = false;

  constructor(private readonly opt: SilenceOptions = DEFAULT_SILENCE_OPTIONS) {}

  push(rms: number, nowMs: number): AutoStopReason | null {
    if (this.startMs === undefined) {
      this.startMs = nowMs;
      this.lastMs = nowMs;
    }
    const dt = nowMs - this.lastMs;
    this.lastMs = nowMs;
    const elapsed = nowMs - this.startMs;

    if (elapsed < this.opt.calibrateMs) {
      this.noiseSum += rms;
      this.noiseCount++;
      this.threshold = Math.min(MAX_THRESHOLD, Math.max(MIN_THRESHOLD, 3 * (this.noiseSum / this.noiseCount)));
    }

    if (rms >= this.threshold) {
      this.speechMs += dt;
      this.silenceMs = 0;
      if (this.speechMs >= this.opt.minSpeechMs) this.spoke = true;
    } else if (this.spoke) {
      this.silenceMs += dt;
    }

    if (elapsed >= this.opt.maxMs) return 'max-duration';
    if (this.spoke && this.silenceMs >= this.opt.silenceMs) return 'silence';
    if (!this.spoke && elapsed >= this.opt.noSpeechMs) return 'no-speech';
    return null;
  }
}
