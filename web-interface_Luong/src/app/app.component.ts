import { Component, ElementRef, OnDestroy, ViewChild, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { ChatMessage, Passage, PipelineStep } from './models/chat.models';
import { AudioRecorderService } from './services/audio-recorder.service';
import { PipelineService } from './services/pipeline.service';

const STEP_LABELS: Record<PipelineStep, string> = {
  idle: 'Hệ thống sẵn sàng',
  recording: 'Đang lắng nghe giọng nói...',
  stt: 'Whisper LoRA đang nhận dạng tiếng Việt...',
  retrieval: 'Đang truy xuất ngữ cảnh (BM25 + e5 + Reranker)...',
  mrc: 'ViT5 đang suy luận câu trả lời...',
  tts: 'Matcha-TTS đang tổng hợp giọng nói...',
  playback: 'Đang phát âm thanh câu trả lời...',
};

type FlowState = 'waiting' | 'active' | 'done';
type AppView = 'chat' | 'library' | 'history' | 'report';

export interface LibraryPassage extends Passage {
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

  @ViewChild('player') private player?: ElementRef<HTMLAudioElement>;
  @ViewChild('chatLog') private chatLog?: ElementRef<HTMLElement>;

  readonly messages = signal<ChatMessage[]>([]);
  readonly step = signal<PipelineStep>('idle');
  readonly error = signal<string | null>(null);
  readonly activeView = signal<AppView>('chat');
  readonly currentlyPlayingUrl = signal<string | null>(null);
  readonly copiedMessageId = signal<number | null>(null);
  readonly selectedCategory = signal<string>('Tất cả');
  readonly currentQueryMode = signal<'voice' | 'text'>('text');

  readonly stepLabels = STEP_LABELS;
  readonly categories = ['Tất cả', 'Văn học', 'Lịch sử', 'Công nghệ', 'Môi trường'];

  readonly flowSteps: ReadonlyArray<{ key: PipelineStep; name: string; description: string; tag: string }> = [
    { key: 'recording', name: 'Ghi âm đầu vào', description: 'Ghi nhận âm thanh PCM 16kHz', tag: 'Audio' },
    { key: 'stt', name: 'Nhận dạng giọng nói', description: 'Whisper-small LoRA (CTranslate2)', tag: 'STT' },
    { key: 'retrieval', name: 'Truy xuất tri thức', description: 'BM25 + Dense e5 + BGE Reranker', tag: 'RAG' },
    { key: 'mrc', name: 'Đọc hiểu suy luận', description: 'Mô hình sinh câu trả lời ViT5-base', tag: 'MRC' },
    { key: 'tts', name: 'Tổng hợp giọng nói', description: 'Matcha-TTS (OT-CFM) + HiFi-GAN', tag: 'TTS' },
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
      voiceQuestions: sessions.filter((session) => session.question.source === 'voice' || session.question.audioUrl).length,
      passages: new Set(sessions.map((session) => session.answer?.passage?.text).filter(Boolean)).size,
    };
  });

  readonly libraryPassages: LibraryPassage[] = [
    {
      id: 'truyen-kieu',
      title: 'Tác phẩm Truyện Kiều & Đại thi hào Nguyễn Du',
      category: 'Văn học',
      level: 'Cơ bản',
      text: 'Truyện Kiều (Đoạn trường tân thanh) là truyện thơ kinh điển của đại thi hào Nguyễn Du, viết bằng chữ Nôm theo thể lục bát gồm 3.254 câu. Hoàn cảnh ra đời: có thuyết nói Nguyễn Du viết sau khi đi sứ Trung Quốc (1814–1820), lại có thuyết nói ông viết trước khi đi sứ vào cuối thời Lê đầu thời Tây Sơn.',
    },
    {
      id: 'environment',
      title: 'Bảo vệ môi trường sống',
      category: 'Môi trường',
      level: 'Trung bình',
      text: 'Việc bảo vệ môi trường sống không chỉ là trách nhiệm của mỗi cá nhân mà còn là nghĩa vụ chung của toàn xã hội, để gìn giữ một tương lai bền vững cho các thế hệ mai sau. Việc giảm thiểu rác thải nhựa và bảo tồn nguồn nước sạch là ưu tiên cấp bách.',
    },
    {
      id: 'history',
      title: 'Di sản văn hóa Việt Nam',
      category: 'Lịch sử',
      level: 'Cơ bản',
      text: 'Di sản văn hóa là tài sản quý giá được hình thành qua nhiều thế hệ. Mỗi di sản lưu giữ những giá trị lịch sử, tri thức và bản sắc riêng của cộng đồng Việt Nam, phản ánh quá trình dựng nước và giữ nước hào hùng.',
    },
    {
      id: 'technology',
      title: 'Trí tuệ nhân tạo trong giáo dục',
      category: 'Công nghệ',
      level: 'Nâng cao',
      text: 'Trí tuệ nhân tạo hỗ trợ người học tiếp cận kiến thức theo nhu cầu cá nhân, đồng thời giúp giáo viên phân tích tiến độ và thiết kế hoạt động học tập phù hợp hơn thông qua các hệ thống đọc hiểu và hỏi đáp đa phương thức.',
    },
    {
      id: 'literature',
      title: 'Giá trị của việc đọc sách',
      category: 'Văn học',
      level: 'Cơ bản',
      text: 'Đọc sách mở rộng hiểu biết, nuôi dưỡng khả năng tưởng tượng và rèn luyện tư duy phản biện. Thói quen đọc đều đặn còn giúp mỗi người diễn đạt suy nghĩ rõ ràng hơn và tích lũy vốn từ phong phú.',
    },
  ];

  passageInput = '';
  private sessionId: string | null = null;
  typedQuestion = '';
  librarySearch = '';

  get busy(): boolean {
    const s = this.step();
    return s !== 'idle' && s !== 'recording' && s !== 'playback';
  }

  setView(view: AppView): void {
    this.activeView.set(view);
  }

  setCategory(cat: string): void {
    this.selectedCategory.set(cat);
  }

  filteredPassages(): LibraryPassage[] {
    const query = this.librarySearch.trim().toLocaleLowerCase('vi');
    const cat = this.selectedCategory();
    let list = this.libraryPassages;
    if (cat !== 'Tất cả') {
      list = list.filter((p) => p.category === cat);
    }
    if (!query) return list;
    return list.filter((p) =>
      `${p.title} ${p.category} ${p.text}`.toLocaleLowerCase('vi').includes(query),
    );
  }

  usePassage(passage: Passage): void {
    this.passageInput = passage.text;
    this.activeView.set('chat');
  }

  useCustomPassage(): void {
    if (this.passageInput.trim()) this.activeView.set('chat');
  }

  clearCustomPassage(): void {
    this.passageInput = '';
  }

  newChat(): void {
    this.resetSession();
    this.messages.set([]);
    this.typedQuestion = '';
    this.error.set(null);
    this.step.set('idle');
  }

  clearHistory(): void {
    this.resetSession();
    this.messages.set([]);
  }

  private resetSession(): void {
    if (this.sessionId) void firstValueFrom(this.pipeline.resetConversation(this.sessionId)).catch(() => undefined);
    this.sessionId = null;
  }

  quickAsk(question: string): void {
    this.typedQuestion = question;
    void this.sendTyped();
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
      this.currentQueryMode.set('voice');
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
        return 'Quyền micro đang bị chặn. Vui lòng cấp quyền Micro trong trình duyệt để sử dụng tính năng giọng nói.';
      case 'NotFoundError':
        return 'Không tìm thấy thiết bị micro trên hệ thống.';
      case 'NotReadableError':
        return 'Micro đang được ứng dụng khác sử dụng hoặc hệ điều hành hạn chế truy cập.';
      default:
        return `Không thể truy cập micro (${error.name}).`;
    }
  }

  async sendTyped(): Promise<void> {
    const question = this.typedQuestion.trim();
    if (!question || this.busy) return;
    this.typedQuestion = '';
    this.error.set(null);
    this.currentQueryMode.set('text');
    try {
      this.push({
        role: 'user',
        text: question,
        source: 'text',
        time: this.nowStr(),
      });
      await this.runFromText(question);
    } catch (e) {
      this.fail(e);
    }
  }

  private async runFromAudio(wav: Blob): Promise<void> {
    const userAudioUrl = this.track(URL.createObjectURL(wav));
    this.currentQueryMode.set('voice');

    this.step.set('stt');
    const question = await firstValueFrom(this.pipeline.transcribe(wav));
    if (!question) throw new Error('Không nhận dạng được câu hỏi, hãy phát âm rõ hơn hoặc nhập bằng văn bản.');
    this.push({
      role: 'user',
      text: question,
      audioUrl: userAudioUrl,
      source: 'voice',
      time: this.nowStr(),
    });

    await this.runFromText(question);
  }

  private async runFromText(question: string): Promise<void> {
    // Một lượt hội thoại: server giữ ngữ cảnh theo session (câu nối tiếp, so sánh, xã giao...).
    this.step.set('retrieval');
    const provided = this.passageInput.trim();
    const res = await firstValueFrom(this.pipeline.ask(question, this.sessionId, provided || undefined));
    this.sessionId = res.session_id;
    const answer = res.answer.trim();
    const passage = res.passage ?? undefined;

    this.step.set('tts');
    const audio = await firstValueFrom(this.pipeline.synthesize(answer));
    const audioUrl = this.track(URL.createObjectURL(audio));
    this.push({
      role: 'bot',
      text: answer,
      audioUrl,
      passage,
      time: this.nowStr(),
    });

    await this.play(audioUrl);
  }

  private async play(url: string): Promise<void> {
    const el = this.player?.nativeElement;
    if (!el) {
      this.step.set('idle');
      this.currentlyPlayingUrl.set(null);
      return;
    }

    this.step.set('playback');
    this.currentlyPlayingUrl.set(url);
    el.src = url;
    el.onended = () => {
      this.currentlyPlayingUrl.set(null);
      this.step.set('idle');
    };
    try {
      await el.play();
    } catch {
      // Autoplay blocked by browser policy
      this.currentlyPlayingUrl.set(null);
      this.step.set('idle');
    }
  }

  toggleAudio(url: string): void {
    const el = this.player?.nativeElement;
    if (!el) return;
    if (this.currentlyPlayingUrl() === url && !el.paused) {
      el.pause();
      this.currentlyPlayingUrl.set(null);
      this.step.set('idle');
      return;
    }
    void this.play(url);
  }

  isPlaying(url?: string): boolean {
    return !!url && this.currentlyPlayingUrl() === url;
  }

  copyText(text: string, msgId?: number): void {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(() => {
      if (msgId !== undefined) {
        this.copiedMessageId.set(msgId);
        setTimeout(() => this.copiedMessageId.set(null), 1800);
      }
    });
  }

  private nowStr(): string {
    const d = new Date();
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
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
    this.currentlyPlayingUrl.set(null);
    if (fallback) return this.error.set(fallback);
    if (e instanceof HttpErrorResponse) {
      const module = e.url?.match(/\/api\/(\w+)/)?.[1] ?? 'server';
      return this.error.set(`Lỗi dịch vụ phân hệ "${module}" (HTTP ${e.status}).`);
    }
    this.error.set(e instanceof Error ? e.message : 'Đã xảy ra lỗi không mong muốn.');
  }

  ngOnDestroy(): void {
    this.objectUrls.forEach((u) => URL.revokeObjectURL(u));
  }
}
