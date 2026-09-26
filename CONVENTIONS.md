# Quy ước đặt tên & Git

## 1. Thư mục

Dạng: `<cong-viec>_<TenNguoiPhuTrach>`

- `<cong-viec>`: chữ thường, kebab-case, tiếng Anh (`speech-to-text`, `text-to-speech`, `retrieval-model`, `mrc-model`, `web-interface`).
- `<TenNguoiPhuTrach>`: một tên, viết hoa chữ đầu, không dấu (`Huy`, `Luong`, `Duy`).
- Thư mục dùng chung không có hậu tố người: `data/`, `docs/`, `scripts/`.
- Không dấu, không khoảng trắng.

Ví dụ: `speech-to-text_Luong/`, `text-to-speech_Duy/`, `retrieval-model_Huy/`.

## 2. File

| Loại | Quy tắc | Ví dụ |
|---|---|---|
| Python | `snake_case.py` | `train_mrc.py`, `stt_client.py` |
| Notebook | `<so-thu-tu>_<mo-ta>.ipynb`, snake_case | `01_finetune_vit5.ipynb` |
| Config | `snake_case.yaml` / `.json` | `train_config.yaml` |
| Tài liệu | `UPPER.md` ở gốc, `kebab-case.md` trong `docs/` | `README.md`, `docs/api-design.md` |
| Model / audio | Không commit (đã ignore); tên: `<model>_<ngay>_<metric>` | `vit5_20260926_em0.62` |

Không dấu, không khoảng trắng, không `final`, `new`, `copy` trong tên file.

## 3. Định danh trong code

- Biến / hàm: `snake_case`. Class: `PascalCase`. Hằng số: `UPPER_SNAKE`.
- Hàm chạy chính của mỗi module đặt theo động từ: `transcribe()`, `synthesize()`, `retrieve()`, `answer_question()`.
- Đầu vào/ra giữa các module là **text thuần (str)** hoặc **đường dẫn audio (`.wav`)**, để STT → Retrieval → MRC → TTS ghép được với nhau.

## 4. Git

### Nhánh

`<loai>/<pham-vi>-<mo-ta-ngan>`, kebab-case.

- Loại: `feat`, `fix`, `docs`, `refactor`, `data`, `exp` (thử nghiệm).
- Phạm vi: `stt`, `tts`, `retrieval`, `mrc`, `web`.

Ví dụ: `feat/mrc-vit5-finetune`, `fix/stt-vietnamese-encoding`, `docs/readme-assignment`.

`main` chỉ nhận merge qua Pull Request; không push trực tiếp.

### Commit

`<loai>(<pham-vi>): <mo-ta-ngan-dong-tu-nguyen-the>`

- Loại như trên, viết thường, tối đa ~72 ký tự dòng đầu.
- Ví dụ: `feat(mrc): add ViT5 seq2seq fine-tune notebook`, `fix(tts): handle empty text input`, `docs: add task assignment`.

Mỗi commit chỉ chứa một việc, chỉ trong thư mục của mình khi có thể.

### Pull Request

- Tiêu đề = dòng commit chính. Mô tả: làm gì, cách chạy/kiểm tra.
- Ít nhất 1 người khác xem trước khi merge.

## 5. Truy vấn nhanh

Tên có cấu trúc để lọc bằng lệnh:

```
git log --grep "(mrc)"        # lịch sử của phần MRC
git branch --list "feat/stt-*"
ls -d *_Huy                   # mọi việc của Huy
```

## 6. Không commit

`data/`, checkpoint (`*.pt`, `*.safetensors`), audio, `.env`/token. Xem [.gitignore](.gitignore).
