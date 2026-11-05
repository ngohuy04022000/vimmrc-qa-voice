// Chạy bởi tests/test_silence_detector.py sau khi biên dịch silence-detector.ts.
import assert from 'node:assert/strict';
import { SilenceDetector } from './silence-detector.js';
const run = (frames) => { // [rms, ms kéo dài], bước 80 ms
  const d = new SilenceDetector(); let t = 0;
  for (const [rms, ms] of frames) for (let k = 0; k < ms; k += 80) { const r = d.push(rms, t); t += 80; if (r) return { r, t }; }
  return { r: null, t };
};
// nói 2 s rồi im: dừng sau ~1,3 s im lặng
let o = run([[0.005, 400], [0.15, 2000], [0.005, 5000]]);
assert.equal(o.r, 'silence'); assert.ok(o.t >= 400 + 2000 + 1300 && o.t <= 400 + 2000 + 1500, String(o.t));
// ngắt quãng ngắn 0,5 s giữa câu không bị cắt
o = run([[0.005, 400], [0.15, 1000], [0.005, 500], [0.15, 1000], [0.005, 5000]]);
assert.equal(o.r, 'silence'); assert.ok(o.t > 400 + 1000 + 500 + 1000 + 1200, String(o.t));
// không nói gì: bỏ cuộc sau 8 s
o = run([[0.005, 20000]]); assert.equal(o.r, 'no-speech'); assert.ok(o.t >= 8000 && o.t < 8200);
// tiếng click 80 ms không tính là đã nói
o = run([[0.005, 400], [0.2, 80], [0.005, 20000]]); assert.equal(o.r, 'no-speech');
// ồn nền cao (0,03): ngưỡng nâng lên 0,06 nên tiếng ồn không giữ phiên mãi
o = run([[0.03, 400], [0.2, 1500], [0.03, 5000]]); assert.equal(o.r, 'silence');
// nói liên tục quá 30 s
o = run([[0.15, 40000]]); assert.equal(o.r, 'max-duration');
console.log('VAD ok');
