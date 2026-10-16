# Tài Liệu 3: Thích Nghi Tiếng Việt & Đổi Mới Tách Thanh Điệu (Tone Decoupling)

> **Thứ tự đọc:** `3 / 5` — Đọc tài liệu này để hiểu chi tiết thiết kế ngôn ngữ học cho tiếng Việt: kỹ thuật tách thanh điệu độc lập, quy trình chuẩn hóa văn bản chuyên biệt cho câu hỏi đáp ViMMRC, và hậu xử lý âm thanh tự nhiên.

---

## 1. Thách Thức Ngôn Ngữ Học Của Tiếng Việt Trong Tổng Hợp Tiếng Nói

Tiếng Việt là ngôn ngữ có thanh điệu (Tonal Language) thuộc ngữ hệ Nam Á. Mỗi âm tiết tiếng Việt đều mang một thanh điệu nhất định, quyết định trực tiếp tới tần số cơ bản ($F_0$ - Pitch Contour) của giọng nói:

| Thanh | Ký hiệu ngữ âm | Mô tả đường cao độ ($F_0$) | Ví dụ từ |
| :---: | :---: | :--- | :--- |
| **Ngang** (Không dấu) | T1 (44) | Cao - bằng phẳng | *ba, ma, ca* |
| **Sắc** | T2 (35) | Bắt đầu trung bình, vút lên cao | *bá, má, cá* |
| **Huyền** | T3 (21) | Bắt đầu thấp, trượt nhẹ xuống dưới | *bà, mà, cà* |
| **Hỏi** | T4 (312) | Xuống thấp rồi vòng ngược lên nhẹ | *bả, mả, cả* |
| **Ngã** | T5 (325) | Đi xuống, gãy/nghẽn thanh quản, rồi vút lên cao | *bã, mã, cã* |
| **Nặng** | T6 (21?) | Xuống rất thấp và bị nghẽn thanh môn đột ngột | *bạ, mạ, cạ* |

```
Tần số F0
  ▲
  │        / Sắc (T2)             \   / Ngã (T5 - gãy thanh quản)
  │  ────── Ngang (T1)             \_/
  │  \                           \  / Hỏi (T4)
  │   \ Huyền (T3)                \/
  │                               \. Nặng (T6 - cụt)
  └────────────────────────────────────────► Thời gian
```

### Hạn chế nghiêm trọng của phương pháp cũ (Ký tự phẳng `char_v1`)
Trong cách biểu diễn truyền thống (như checkpoint VIVOS V1 ban đầu), mỗi ký tự mang dấu được xem là một token riêng biệt:
- Ký tự `a` sinh ra 6 token: `a`, `à`, `á`, `ả`, `ã`, `ạ`.
- Tương tự với các nguyên âm khác: `ă`, `â`, `e`, `ê`, `i`, `o`, `ô`, `ơ`, `u`, `ư`, `y`...
- **Hệ quả**: Bộ từ vựng phình to lên tới **91 token**.
- **Loãng dữ liệu nghiêm trọng**: Mô hình phải học thanh "huyền" hàng chục lần một cách rời rạc trên từng nguyên âm độc lập. Với các nguyên âm kép hoặc tổ hợp ít gặp (như `uở`, `oẹ`, `iễ`...), mô hình gần như không được huấn luyện đủ, dẫn tới hiện tượng **đọc sai dấu, mất thanh hoặc ngọng giọng**.

---

## 2. Kỹ Thuật Tách Thanh Điệu Độc Lập (Tone Decoupling, `vi_tone_v2`)

Để giải quyết triệt để vấn đề trên, dự án đã thiết kế bộ Frontend tiếng Việt mới [src/vi_frontend.py](file:///d:/Project/vimmrc-qa-voice/text-to-speech_Duy/src/vi_frontend.py) dựa trên nguyên lý **tách rời âm vị và thanh điệu**.

### 2.1. Phân biệt Dấu Âm Vị vs Dấu Thanh Điệu
Trong chữ Quốc ngữ, ta cần phân biệt rạch ròi 2 loại dấu:
1. **Dấu âm vị (Phonemic Diacritics)**: Các dấu mũ, râu (*ă, â, ê, ô, ơ, ư*) biến đổi bản chất của nguyên âm (khẩu hình miệng, vị trí lưỡi). **Các ký tự này bắt buộc phải được giữ nguyên** vì chúng là các âm vị khác nhau.
2. **Dấu thanh điệu (Tone Diacritics)**: 5 dấu (*sắc, huyền, hỏi, ngã, nặng*) chỉ quy định đường biến thiên cao độ $F_0$. **Các dấu này được bóc tách hoàn toàn khỏi nguyên âm**.

### 2.2. Bảng mã hóa 6 thanh điệu (0 đến 5)
Mỗi thanh điệu được chuẩn hóa thành một số nguyên từ `0` đến `5` và đặt ở **vị trí cuối cùng của âm tiết**:

| Mã Token | Tên thanh | Dấu Quốc ngữ | Vị trí đặt |
| :---: | :--- | :---: | :--- |
| `0` | Thanh Ngang (Không dấu) | Không | Cuối âm tiết |
| `1` | Thanh Sắc | `´` | Cuối âm tiết |
| `2` | Thanh Huyền | ``` | Cuối âm tiết |
| `3` | Thanh Hỏi | `̉` | Cuối âm tiết |
| `4` | Thanh Ngã | `˜` | Cuối âm tiết |
| `5` | Thanh Nặng | `.` | Cuối âm tiết |

### 2.3. Quy trình biến đổi âm tiết (Ví dụ thực tế)
Thuật toán sử dụng phân tách chuẩn Unicode NFD (`unicodedata.normalize('NFD', ...)`), nhận diện dấu thanh theo mã Unicode Combining Characters (`\u0300`, `\u0301`, `\u0303`, `\u0309`, `\u0323`), loại bỏ dấu khỏi nguyên âm và chèn mã thanh vào cuối từ:

```
Văn bản gốc:   "Thủ đô Hà Nội có Hồ Gươm"
               │
Bước 1: NFD & Tách thanh:
  Thủ   ──>  T - h - u  + Thanh Hỏi (3)    ──>  [t, h, u, 3]
  đô    ──>  đ - ô      + Thanh Ngang (0)  ──>  [đ, ô, 0]
  Hà    ──>  h - a      + Thanh Huyền (2)  ──>  [h, a, 2]
  Nội   ──>  n - ô - i  + Thanh Nặng (5)   ──>  [n, ô, i, 5]
  có    ──>  c - o      + Thanh Sắc (1)    ──>  [c, o, 1]
  Hồ    ──>  h - ô      + Thanh Huyền (2)  ──>  [h, ô, 2]
  Gươm  ──>  g - ư - ơ - m + Thanh Ngang (0) ──> [g, ư, ơ, m, 0]

Kết quả Token: [t, h, u, 3, " ", đ, ô, 0, " ", h, a, 2, " ", n, ô, i, 5, ...]
```

### 2.4. Ưu thế vượt trội của `vi_tone_v2`
1. **Thu nhỏ kích thước từ vựng**: Giảm từ **91 token xuống còn đúng 41 token** (29 chữ cái tiếng Việt cơ bản + 6 mã thanh điệu + dấu cách + 5 dấu câu/blank).
2. **Tăng mật độ dữ liệu huấn luyện (Data Density)**: Token thanh huyền `2` được huấn luyện đồng thời trên tất cả các từ có dấu huyền (*bà, cà, gà, nhà, trường, người...*), thay vì bị chia nhỏ thành từng embedding riêng.
3. **Cơ chế Self-Attention nắm bắt thanh điệu**: Bằng cách đặt token thanh điệu ở cuối âm tiết, khối Transformer Encoder sử dụng Attention đa đầu để điều khiển toàn bộ trường biểu diễn âm học của phần vần đi trước, tái tạo đường cong cao độ $F_0$ chuẩn xác 100%.

---

## 3. Module Chuẩn Hóa Văn Bản Tiếng Việt (`src/normalizer.py`)

Trong ứng dụng hỏi đáp ViMMRC, văn bản đầu vào từ mô hình MRC chứa rất nhiều ký hiệu đặc thù (nhãn đáp án trắc nghiệm, số liệu, đơn vị đo lường, ngày tháng). Nếu đưa trực tiếp vào mô hình TTS, mô hình sẽ đọc sai hoặc bỏ qua.

Module `normalize_vietnamese_text()` thực hiện chuẩn hóa toàn diện theo các luật:

### 3.1. Nhãn đáp án trắc nghiệm
- `(A) Chiến thắng...` $\rightarrow$ `Đáp án A: Chiến thắng...`
- `**Đáp án:** B.` $\rightarrow$ `Đáp án B:`
- `C: Tốc độ...` $\rightarrow$ `Đáp án C: Tốc độ...`

### 3.2. Số đếm và số thập phân
- Số nguyên: `125` $\rightarrow$ `một trăm hai mươi lăm`
- Số thập phân: `98.5%` $\rightarrow$ `chín mươi tám phẩy năm phần trăm`
- Số có dấu phân cách hàng nghìn: `250.000` $\rightarrow$ `hai trăm năm mươi nghìn`

### 3.3. Đơn vị đo lường và tiền tệ
- Đơn vị: `120 km/h` $\rightarrow$ `một trăm hai mươi ki-lô-mét trên giờ`
- Diện tích: `1.500 km2` $\rightarrow$ `một nghìn năm trăm ki-lô-mét vuông`
- Nhiệt độ: `35°C` $\rightarrow$ `ba mươi lăm độ C`
- Tiền tệ: `250.000 VND` $\rightarrow$ `hai trăm năm mươi nghìn đồng`, `10 USD` $\rightarrow$ `mười đô la`

### 3.4. Ngày tháng & Thời gian
- Định dạng ngày: `07/05/1954` $\rightarrow$ `ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư`
- Định dạng giờ: `08:30` $\rightarrow$ `tám giờ ba mươi phút`

### 3.5. Chữ cái ngoại lai & Ký tự viết tắt
- Chữ ngoại lai được phiên âm tương đương: `f` $\rightarrow$ `ph`, `j` $\rightarrow$ `gi`, `w` $\rightarrow$ `u`, `z` $\rightarrow$ `d`.
- Các từ viết tắt thông dụng: `TP.` $\rightarrow$ `thành phố`, `TS.` $\rightarrow$ `tiến sĩ`, `PGS.` $\rightarrow$ `phó giáo sư`.

---

## 4. Hậu Xử Lý Khi Suy Luận (`src/matcha_engine.py`)

Các tập dữ liệu âm thanh tiếng Việt (như InfoRe1 hay VIVOS) đều được thu âm dưới dạng các câu đơn lẻ, văn bản không có dấu câu. Do đó mô hình không thể tự học được cách ngắt câu dài.

Để câu đọc trong hệ thống Q&A có ngữ điệu tự nhiên như người thật, Engine thực hiện 3 bước hậu xử lý:

### 4.1. Phân đoạn câu & Chèn khoảng lặng ngắt nghỉ (Prosodic Pauses)
Engine tự động phân tách câu văn thành các cụm nhỏ theo dấu câu và chèn các khoảng lặng nhân tạo phù hợp:
- Sau dấu phẩy `,`: chèn khoảng lặng **0.15 giây** (nghỉ ngắn giữa các ý).
- Sau dấu chấm phẩy `;` hoặc hai chấm `:`: chèn **0.25 giây**.
- Sau dấu kết thúc câu `.`, `!`, `?`, `…`: chèn **0.40 giây** (nghỉ hết câu).
- Sau dấu xuống dòng `\n`: chèn **0.45 giây**.

### 4.2. Cắt nhiễu khoảng lặng biên (Trim Silence & Cross-fade)
- Tại điểm nối giữa các cụm câu, engine áp dụng hàm `_trim_silence()` với ngưỡng năng lượng **−30 dB** so với đỉnh và giữ lại biên đệm 50ms để không bị mất phụ âm cuối.
- Áp dụng kỹ thuật làm mượt biên (Fade-in / Fade-out 10ms) ở đầu và đuôi file để triệt tiêu hoàn toàn tiếng "tách" (click artifacts) khi ghép nối âm thanh.
- Chuẩn hóa âm lượng đầu ra đạt chuẩn **−1 dBFS**, giúp âm thanh phát ra to, rõ ràng và không bị vỡ tiếng (clipping).

---

*Xem tiếp tài liệu kế tiếp để tìm hiểu chi tiết về quy trình huấn luyện và tối ưu Vocoder: **[`4_quy_trinh_huan_luyen_va_vocoder_hifigan.md`](4_quy_trinh_huan_luyen_va_vocoder_hifigan.md)**.*
