import { Component, ElementRef, OnDestroy, ViewChild, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AnswerKind, ChatMessage, Passage, PipelineStep } from './models/chat.models';
import { AudioRecorderService } from './services/audio-recorder.service';
import { PipelineService } from './services/pipeline.service';

const STEP_LABELS: Record<PipelineStep, string> = {
  idle: 'Sẵn sàng',
  recording: 'Đang thu âm...',
  stt: 'Whisper đang nhận dạng giọng nói...',
  retrieval: 'Đang hiểu câu hỏi và tìm đoạn văn liên quan...',
  mrc: 'Mô hình đang đọc hiểu và soạn câu trả lời...',
  tts: 'Đang tổng hợp giọng nói...',
  playback: 'Đang phát câu trả lời...',
};

type FlowState = 'waiting' | 'active' | 'done';

const KIND_LABELS: Record<AnswerKind, string> = {
  qa: 'Câu trả lời',
  multi: 'Trả lời từng ý',
  compare: 'So sánh',
  yesno: 'Đúng / sai',
  summary: 'Tóm tắt đoạn văn',
  expand: 'Giải thích thêm',
  smalltalk: 'Trò chuyện',
  math: 'Phép tính',
  unknown: 'Chưa tìm thấy',
};
type AppView = 'chat' | 'library' | 'history' | 'report';

interface LibraryPassage extends Passage {
  id: string;
  title: string;
  category: string;
  level: string;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnDestroy {
  private readonly recorder = inject(AudioRecorderService);
  private readonly pipeline = inject(PipelineService);
  private readonly objectUrls: string[] = [];
  private nextId = 1;
  /** Phiên hội thoại phía server, để hiểu câu nối tiếp như "còn Hàn Quốc thì sao?". */
  private sessionId: string | null = null;

  @ViewChild('player') private player?: ElementRef<HTMLAudioElement>;
  @ViewChild('chatLog') private chatLog?: ElementRef<HTMLElement>;

  readonly messages = signal<ChatMessage[]>([]);
  readonly step = signal<PipelineStep>('idle');
  readonly error = signal<string | null>(null);
  readonly activeView = signal<AppView>('chat');
  readonly stepLabels = STEP_LABELS;
  readonly kindLabels = KIND_LABELS;
  readonly flowSteps: ReadonlyArray<{ key: PipelineStep; name: string; description: string; icon: string }> = [
    { key: 'recording', name: 'Thu âm', description: 'Ghi nhận giọng nói của bạn', icon: '♬' },
    { key: 'stt', name: 'Speech-to-Text', description: 'Whisper chuyển giọng nói thành văn bản', icon: 'Aa' },
    { key: 'retrieval', name: 'Retrieval', description: 'Tìm kiếm đoạn văn phù hợp', icon: '⌕' },
    { key: 'mrc', name: 'MRC Inference', description: 'Suy luận câu trả lời từ ngữ cảnh', icon: 'AI' },
    { key: 'tts', name: 'Text-to-Speech', description: 'Tổng hợp giọng nói trả lời', icon: '♪' },
  ];
  readonly latestPassage = computed(() =>
    [...this.messages()].reverse().find((message) => message.passage)?.passage,
  );
  readonly learningSessions = computed(() => {
    const sessions: Array<{ id: number; question: ChatMessage; answer?: ChatMessage }> = [];
    for (const message of this.messages()) {
      if (message.role === 'user') {
        sessions.push({ id: message.id, question: message });
      } else if (sessions.length > 0 && !sessions.at(-1)?.answer) {
        sessions[sessions.length - 1].answer = message;
      }
    }
    return sessions.reverse();
  });
  readonly reportMetrics = computed(() => {
    const sessions = this.learningSessions();
    return {
      questions: sessions.length,
      answered: sessions.filter((session) => session.answer).length,
      voiceQuestions: sessions.filter((session) => session.question.audioUrl).length,
      passages: new Set(sessions.map((session) => session.answer?.passage?.text).filter(Boolean)).size,
    };
  });
  readonly libraryPassages: LibraryPassage[] = [
    {
      id: 'environment',
      title: 'Bảo vệ môi trường sống',
      category: 'Môi trường',
      level: 'Trung bình',
      text: 'Việc bảo vệ môi trường sống không chỉ là trách nhiệm của mỗi cá nhân mà còn là nghĩa vụ chung của toàn xã hội, để gìn giữ một tương lai bền vững cho các thế hệ mai sau.',
    },
    {
      id: 'history',
      title: 'Di sản văn hóa Việt Nam',
      category: 'Lịch sử',
      level: 'Cơ bản',
      text: 'Di sản văn hóa là tài sản quý giá được hình thành qua nhiều thế hệ. Mỗi di sản lưu giữ những giá trị lịch sử, tri thức và bản sắc riêng của cộng đồng Việt Nam.',
    },
    {
      id: 'technology',
      title: 'Trí tuệ nhân tạo trong giáo dục',
      category: 'Công nghệ',
      level: 'Nâng cao',
      text: 'Trí tuệ nhân tạo hỗ trợ người học tiếp cận kiến thức theo nhu cầu cá nhân, đồng thời giúp giáo viên phân tích tiến độ và thiết kế hoạt động học tập phù hợp hơn.',
    },
    {
      id: 'literature',
      title: 'Giá trị của việc đọc sách',
      category: 'Văn học',
      level: 'Cơ bản',
      text: 'Đọc sách mở rộng hiểu biết, nuôi dưỡng khả năng tưởng tượng và rèn luyện tư duy phản biện. Thói quen đọc đều đặn còn giúp mỗi người diễn đạt suy nghĩ rõ ràng hơn.',
    },
  ];

  /** Optional passage provided by the user; when set, retrieval is skipped. */
  passageInput = '';
  typedQuestion = '';
  librarySearch = '';

  get busy(): boolean {
    const s = this.step();
    return s !== 'idle' && s !== 'recording' && s !== 'playback';
  }

  setView(view: AppView): void {
    this.activeView.set(view);
  }

  filteredPassages(): LibraryPassage[] {
    const query = this.librarySearch.trim().toLocaleLowerCase('vi');
    if (!query) return this.libraryPassages;
    return this.libraryPassages.filter((passage) =>
      `${passage.title} ${passage.category} ${passage.text}`.toLocaleLowerCase('vi').includes(query),
    );
  }

  usePassage(passage: Passage): void {
    this.passageInput = passage.text;
    this.activeView.set('chat');
  }

  useCustomPassage(): void {
    if (this.passageInput.trim()) this.activeView.set('chat');
  }

  clearHistory(): void {
    this.messages.set([]);
    if (this.sessionId) {
      this.pipeline.resetConversation(this.sessionId).subscribe({ error: () => undefined });
      this.sessionId = null;
    }
  }

  flowState(target: PipelineStep): FlowState {
    const current = this.step();
    const targetIndex = this.flowSteps.findIndex((item) => item.key === target);
    const currentIndex = this.flowSteps.findIndex((item) => item.key === current);
    if (current === 'idle' || current === 'playback') {
      return this.messages().some((message) => message.role === 'bot') ? 'done' : 'waiting';
    }
    if (current === target) return 'active';
    return targetIndex < currentIndex ? 'done' : 'waiting';
  }

  async toggleRecording(): Promise<void> {
    this.error.set(null);
    if (this.step() === 'recording') {
      try {
        const wav = await this.recorder.stop();
        await this.runFromAudio(wav);
      } catch (e) {
        this.fail(e);
      }
      return;
    }

    try {
      await this.recorder.start();
      this.step.set('recording');
    } catch (e) {
      this.fail(e, this.microphoneError(e));
    }
  }

  private microphoneError(error: unknown): string {
    if (!(error instanceof DOMException)) {
      return error instanceof Error ? error.message : 'Không truy cập được micro.';
    }

    switch (error.name) {
      case 'NotAllowedError':
        return 'Quyền micro đang bị chặn. Mở biểu tượng khóa cạnh thanh địa chỉ, cho phép Micro rồi tải lại trang.';
      case 'NotFoundError':
        return 'Không tìm thấy micro trên thiết bị.';
      case 'NotReadableError':
        return 'Micro đang được ứng dụng khác sử dụng hoặc hệ điều hành đang chặn truy cập.';
      default:
        return `Không truy cập được micro (${error.name}).`;
    }
  }

  async sendTyped(): Promise<void> {
    const question = this.typedQuestion.trim();
    if (!question || this.busy) return;
    this.typedQuestion = '';
    this.error.set(null);
    try {
      this.push({ role: 'user', text: question });
      await this.runFromText(question);
    } catch (e) {
      this.fail(e);
    }
  }

  private async runFromAudio(wav: Blob): Promise<void> {
    const userAudioUrl = this.track(URL.createObjectURL(wav));

    this.step.set('stt');
    const question = await firstValueFrom(this.pipeline.transcribe(wav));
    if (!question) throw new Error('Không nhận dạng được câu hỏi, hãy nói lại rõ hơn.');
    this.push({ role: 'user', text: question, audioUrl: userAudioUrl });

    await this.runFromText(question);
  }

  private async runFromText(question: string): Promise<void> {
    const provided = this.passageInput.trim();
    this.step.set(provided ? 'mrc' : 'retrieval');
    const reply = await firstValueFrom(this.pipeline.ask(question, this.sessionId, provided || undefined));
    this.sessionId = reply.session_id;
    const passage: Passage | undefined = reply.passage ?? undefined;
    const resolved = reply.resolved_question?.trim();
    const rewritten = resolved && resolved.toLocaleLowerCase('vi') !== question.trim().replace(/[?.!]+$/, '').toLocaleLowerCase('vi');

    this.step.set('tts');
    let audioUrl: string | undefined;
    try {
      const audio = await firstValueFrom(this.pipeline.synthesize(reply.answer));
      audioUrl = this.track(URL.createObjectURL(audio));
    } catch {
      // TTS lỗi (mất mạng, chưa có checkpoint): vẫn hiện câu trả lời dạng chữ.
      this.error.set('Không tổng hợp được giọng nói, câu trả lời chỉ hiển thị dạng chữ.');
    }
    this.push({
      role: 'bot',
      text: reply.answer,
      audioUrl,
      passage,
      kind: reply.kind,
      resolvedQuestion: rewritten && reply.kind !== 'smalltalk' ? resolved : undefined,
    });

    if (audioUrl) await this.play(audioUrl);
    else this.step.set('idle');
  }

  private async play(url: string): Promise<void> {
    const el = this.player?.nativeElement;
    if (!el) return this.step.set('idle');

    this.step.set('playback');
    el.src = url;
    el.onended = () => this.step.set('idle');
    try {
      await el.play();
    } catch {
      // Autoplay blocked: the user can still press play on the message.
      this.step.set('idle');
    }
  }

  replay(url: string): void {
    void this.play(url);
  }

  private push(msg: Omit<ChatMessage, 'id'>): void {
    this.messages.update((list) => [...list, { ...msg, id: this.nextId++ }]);
    queueMicrotask(() => {
      const el = this.chatLog?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    });
  }

  private track(url: string): string {
    this.objectUrls.push(url);
    return url;
  }

  private fail(e: unknown, fallback?: string): void {
    this.step.set('idle');
    if (fallback) return this.error.set(fallback);
    if (e instanceof HttpErrorResponse) {
      const module = e.url?.match(/\/api\/(\w+)/)?.[1] ?? 'server';
      return this.error.set(`Lỗi khi gọi module "${module}" (HTTP ${e.status}).`);
    }
    this.error.set(e instanceof Error ? e.message : 'Đã xảy ra lỗi không xác định.');
  }

  ngOnDestroy(): void {
    this.objectUrls.forEach((u) => URL.revokeObjectURL(u));
  }
}
