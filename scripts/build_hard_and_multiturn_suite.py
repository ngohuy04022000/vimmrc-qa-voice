"""Generate and validate the Hard Questions and Multi-Turn Long Dialogue Benchmark Suite.

Includes:
1. 35 Hard & Complex Questions (Multi-hop, Comparative, Cause-and-Effect, Technical Depth)
2. 4 Full-length Multi-turn Conversational Scenarios (30 continuous dialogue turns with anaphora & context tracking)
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "hard_and_multiturn_suite.json"

HARD_QUESTIONS = [
    # --- Category 1: Lịch sử & Nhân vật (Multi-hop & Nguyên nhân - Hệ quả) ---
    {
        "id": "HARD_HIST_001",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Ai là người chỉ huy chiến dịch đại phá 29 vạn quân Thanh vào năm 1789 và ông đã lên ngôi Hoàng đế tại đâu trước khi xuất quân?",
        "reference_answer": "Vua Quang Trung (Nguyễn Huệ) là người chỉ huy, và ông đã làm lễ lên ngôi Hoàng đế tại núi Bân (Huế) vào ngày 25 tháng 11 năm Mậu Thân trước khi xuất quân ra Bắc.",
        "expected_passage_id": "kb:deep_history_quangtrung",
    },
    {
        "id": "HARD_HIST_002",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "cause_and_effect",
        "question": "Trong chiến dịch Tết Kỷ Dậu 1789, trận tập kích bất ngờ nào vào đồn Khương Thượng đã khiến tướng giặc Sầm Nghi Đống phải khiếp sợ thắt cổ tự tử?",
        "reference_answer": "Trận tập kích bất ngờ vào đồn Khương Thượng Đống Đa do Đô đốc Đặng Tiến Đông chỉ huy đã khiến thái thú Sầm Nghi Đống khiếp sợ và thắt cổ tự tử trên núi Loa.",
        "expected_passage_id": "kb:deep_history_quangtrung",
    },
    {
        "id": "HARD_HIST_003",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "technical_depth",
        "question": "Nghệ thuật hành quân thần tốc của vua Quang Trung từ Phú Xuân ra Thăng Long được tổ chức với chiến thuật đặc biệt nào để giữ sức cho binh sĩ?",
        "reference_answer": "Quân lính được chia thành từng tốp ba người, hai người thay phiên nhau gánh cáng một người nghỉ ngơi luân phiên ngày đêm, đồng thời tuyển thêm quân ở Nghệ An và Thanh Hóa.",
        "expected_passage_id": "kb:deep_history_quangtrung",
    },
    {
        "id": "HARD_HIST_004",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Sau khi đánh tan quân Thanh, vua Quang Trung đã ban hành chiếu chỉ gì và thành lập cơ quan nào do danh sĩ La Sơn Phu Tử Nguyễn Thiếp đứng đầu để phát triển văn hóa giáo dục?",
        "reference_answer": "Vua Quang Trung ban hành Chiếu khuyến học và thành lập Viện Sùng chính do La Sơn Phu Tử Nguyễn Thiếp đứng đầu nhằm dịch sách chữ Hán sang chữ Nôm.",
        "expected_passage_id": "kb:deep_history_quangtrung",
    },
    {
        "id": "HARD_HIST_005",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "comparative",
        "question": "So sánh trận Bạch Đằng năm 938 của Ngô Quyền và trận Bạch Đằng năm 1288 của Trần Hưng Đạo, hai vị anh hùng dân tộc này đã đánh bại kẻ thù xâm lược nào?",
        "reference_answer": "Năm 938 Ngô Quyền đánh bại quân Nam Hán chấm dứt nghìn năm Bắc thuộc, còn năm 1288 Hưng Đạo Đại Vương Trần Quốc Tuấn lãnh đạo quân dân Đại Việt đánh tan quân xâm lược Mông Nguyên.",
        "expected_passage_id": "kb:supplement_history",
    },
    {
        "id": "HARD_HIST_006",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Vị vua nào đã ban Chiếu dời đô từ Hoa Lư về Thăng Long vào năm 1010 và tên kinh đô mới có ý nghĩa hình tượng là gì?",
        "reference_answer": "Vua Lý Thái Tổ ban Chiếu dời đô từ Hoa Lư về thành Đại La và đổi tên thành Thăng Long với hình tượng rồng vàng bay lên.",
        "expected_passage_id": "kb:supplement_history",
    },
    {
        "id": "HARD_HIST_007",
        "category": "Lịch sử Việt Nam",
        "reasoning_type": "cause_and_effect",
        "question": "Chiến thắng Điện Biên Phủ vào ngày 7 tháng 5 năm 1954 có ý nghĩa lịch sử to lớn như thế nào đối với cuộc kháng chiến chống thực dân Pháp?",
        "reference_answer": "Chiến thắng lịch sử Điện Biên Phủ toàn thắng ngày 7 tháng 5 năm 1954 lừng lẫy năm châu chấn động địa cầu, đập tan tập đoàn cứ điểm mạnh nhất của Pháp và buộc Pháp phải ký Hiệp định Genève.",
        "expected_passage_id": "kb:supplement_history",
    },

    # --- Category 2: Địa lý & Kỳ quan (So sánh & Đặc điểm không gian) ---
    {
        "id": "HARD_GEO_001",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Đỉnh núi Fansipan cao chính xác bao nhiêu mét, thuộc dãy núi nào và được hình thành từ kỷ địa chất nào trong lịch sử kiến tạo?",
        "reference_answer": "Đỉnh Fansipan cao chính xác 3.143 mét thuộc dãy Hoàng Liên Sơn, được hình thành trong đợt uốn nếp kiến tạo vào kỷ Permi - Trias cách đây hàng trăm triệu năm.",
        "expected_passage_id": "kb:deep_geography_wonders",
    },
    {
        "id": "HARD_GEO_002",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "technical_depth",
        "question": "Hang Sơn Đoòng có kích thước thể tích ước tính đạt bao nhiêu triệu mét khối và bên trong hang có các cấu trúc địa chất, sinh thái đặc biệt nào?",
        "reference_answer": "Hang Sơn Đoòng có thể tích ước tính đạt 38.5 triệu mét khối, sở hữu sông ngầm, cột thạch nhũ cao tới 70 mét và hai hố sụt lớn nuôi dưỡng khu rừng nhiệt đới nguyên sinh Vườn Địa Đàng.",
        "expected_passage_id": "kb:deep_geography_wonders",
    },
    {
        "id": "HARD_GEO_003",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Ai là người địa phương đầu tiên phát hiện ra hang Sơn Đoòng vào năm 1991 và đoàn thám hiểm quốc tế nào đã khảo sát công bố hang vào năm 2009?",
        "reference_answer": "Người dân địa phương Hồ Khanh phát hiện lần đầu tiên vào năm 1991, và đoàn thám hiểm Hiệp hội Hang động Hoàng gia Anh (BCRA) do Howard Limbert dẫn đầu khảo sát công bố năm 2009.",
        "expected_passage_id": "kb:deep_geography_wonders",
    },
    {
        "id": "HARD_GEO_004",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "comparative",
        "question": "Phân biệt giữa sông Đồng Nai và sông Mê Kông chảy qua Việt Nam về đặc điểm chiều dài lưu vực nội địa?",
        "reference_answer": "Sông Đồng Nai là con sông nội địa dài nhất chỉ chảy trong lãnh thổ Việt Nam, trong khi sông Mê Kông là con sông quốc tế lớn nhất chảy qua Nam Bộ đổ ra biển qua chín cửa sông Cửu Long.",
        "expected_passage_id": "kb:supplement_geography",
    },
    {
        "id": "HARD_GEO_005",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "multi_hop",
        "question": "Hòn đảo nào có diện tích lớn nhất Việt Nam, thuộc tỉnh nào và được mệnh danh là Đảo Ngọc?",
        "reference_answer": "Đảo Phú Quốc thuộc tỉnh Kiên Giang là hòn đảo lớn nhất Việt Nam và được mệnh danh là Đảo Ngọc.",
        "expected_passage_id": "kb:supplement_geography",
    },
    {
        "id": "HARD_GEO_006",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "cause_and_effect",
        "question": "Tại sao đỉnh Fansipan vào mùa đông lại có hiện tượng băng giá và tuyết rơi dù Việt Nam nằm trong vành đai nhiệt đới gió mùa?",
        "reference_answer": "Do độ cao địa hình vượt trội 3.143 mét mang đặc trưng khí hậu ôn đới núi cao, nhiệt độ giảm mạnh theo độ cao kết hợp với các đợt không khí lạnh cực mạnh từ phương Bắc tràn về.",
        "expected_passage_id": "kb:deep_geography_wonders",
    },
    {
        "id": "HARD_GEO_007",
        "category": "Địa lý Việt Nam",
        "reasoning_type": "comparative",
        "question": "Vịnh Hạ Long được UNESCO công nhận là di sản thiên nhiên thế giới nhờ sở hữu cảnh quan địa chất đặc trưng gì?",
        "reference_answer": "Vịnh Hạ Long thuộc tỉnh Quảng Ninh nổi tiếng với cảnh quan địa hình karst đá vôi ngập nước kỳ vĩ gồm hàng nghìn hòn đảo lớn nhỏ được hình thành qua hàng triệu năm.",
        "expected_passage_id": "kb:supplement_geography",
    },

    # --- Category 3: Khoa học & Đời sống (Cơ chế & Định lượng) ---
    {
        "id": "HARD_SCI_001",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "technical_depth",
        "question": "Viết phương trình hóa học tổng quát của quá trình quang hợp ở thực vật và cho biết năng lượng ánh sáng được hấp thụ bởi sắc tố nào?",
        "reference_answer": "Phương trình tổng quát là 6CO2 + 6H2O -> C6H12O6 + 6O2, và năng lượng ánh sáng Mặt Trời được hấp thụ bởi sắc tố diệp lục (chlorophyll) trong lục lạp.",
        "expected_passage_id": "kb:deep_science_biology",
    },
    {
        "id": "HARD_SCI_002",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "cause_and_effect",
        "question": "Tại sao vào ban đêm trong phòng ngủ đóng kín cửa không nên để quá nhiều chậu cây xanh?",
        "reference_answer": "Vì ban đêm không có ánh sáng nên quang hợp ngừng lại, cây xanh chỉ hô hấp tế bào tiêu thụ khí oxy và thải ra khí carbon dioxide gây nguy cơ thiếu dưỡng khí cho con người.",
        "expected_passage_id": "kb:deep_science_biology",
    },
    {
        "id": "HARD_SCI_003",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "comparative",
        "question": "So sánh hai bào quan lục lạp và ty thể trong tế bào thực vật về vai trò chuyển hóa năng lượng?",
        "reference_answer": "Lục lạp thực hiện quá trình quang hợp hấp thụ năng lượng ánh sáng để tổng hợp đường glucose và sinh oxy, còn ty thể thực hiện hô hấp tế bào oxy hóa glucose để giải phóng năng lượng ATP.",
        "expected_passage_id": "kb:deep_science_biology",
    },
    {
        "id": "HARD_SCI_004",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "technical_depth",
        "question": "Nước tinh khiết sôi ở 100 độ C ở áp suất tiêu chuẩn bao nhiêu và nhiệt độ sôi của nước thay đổi thế nào khi lên vùng núi cao áp suất thấp?",
        "reference_answer": "Nước sôi ở 100 độ C ở áp suất 1 atm tiêu chuẩn, và khi lên vùng núi cao áp suất khí quyển giảm thì nhiệt độ sôi của nước sẽ giảm xuống dưới 100 độ C.",
        "expected_passage_id": "kb:supplement_science",
    },
    {
        "id": "HARD_SCI_005",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "multi_hop",
        "question": "Vận tốc ánh sáng truyền trong chân không là bao nhiêu km/s và ánh sáng từ Mặt Trời mất khoảng bao lâu để truyền tới Trái Đất?",
        "reference_answer": "Vận tốc ánh sáng trong chân không xấp xỉ 300.000 km/s và ánh sáng Mặt Trời mất khoảng 8 phút 20 giây để truyền tới Trái Đất.",
        "expected_passage_id": "kb:supplement_science",
    },
    {
        "id": "HARD_SCI_006",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "comparative",
        "question": "Hành tinh nào gần Mặt Trời nhất và hành tinh nào có khối lượng lớn nhất trong Hệ Mặt Trời của chúng ta?",
        "reference_answer": "Sao Thủy (Mercury) là hành tinh gần Mặt Trời nhất, còn Sao Mộc (Jupiter) là hành tinh có kích thước và khối lượng lớn nhất trong Hệ Mặt Trời.",
        "expected_passage_id": "kb:supplement_science",
    },
    {
        "id": "HARD_SCI_007",
        "category": "Khoa học & Đời sống",
        "reasoning_type": "technical_depth",
        "question": "Tổng số đo ba góc trong của một hình tam giác trong hình học phẳng Euclid luôn bằng bao nhiêu độ và bằng bao nhiêu radian?",
        "reference_answer": "Tổng ba góc trong của một hình tam giác luôn bằng 180 độ, tương đương với pi radian.",
        "expected_passage_id": "kb:supplement_science",
    },

    # --- Category 4: Văn học & Văn hóa (Đối sánh nghệ thuật & Giá trị nhân đạo) ---
    {
        "id": "HARD_LIT_001",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "comparative",
        "question": "Trong kiệt tác Truyện Kiều, Nguyễn Du đã sử dụng bút pháp ước lệ tượng trưng đối sánh vẻ đẹp và dự báo số phận của Thúy Kiều và Thúy Vân như thế nào?",
        "reference_answer": "Thúy Vân đoan trang phúc hậu 'mây thua tuyết nhường' dự báo cuộc đời êm đềm bình lặng; còn Thúy Kiều sắc sảo mặn mà 'hoa ghen liễu hờn' khiến tạo hóa đố kỵ dự báo số phận mười lăm năm truân chuyên.",
        "expected_passage_id": "kb:deep_literature_culture",
    },
    {
        "id": "HARD_LIT_002",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "multi_hop",
        "question": "Tác phẩm Truyện Kiều gồm bao nhiêu câu thơ, được viết theo thể thơ gì và bằng loại văn tự truyền thống nào của dân tộc ta?",
        "reference_answer": "Truyện Kiều gồm tổng cộng 3.254 câu thơ, được viết theo thể thơ lục bát truyền thống bằng chữ Nôm.",
        "expected_passage_id": "kb:deep_literature_culture",
    },
    {
        "id": "HARD_LIT_003",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "cause_and_effect",
        "question": "Trong truyện ngắn Lão Hạc của Nam Cao, tại sao lão Hạc lại quyết định bán con chó Vàng và sau đó ăn bả chó tự tử?",
        "reference_answer": "Lão Hạc bán cậu Vàng vì không đủ tiền nuôi và tự tử bằng bả chó để giữ trọn mảnh vườn cùng số tiền dành dụm lại cho con trai đi phu đồn điền cao su trở về.",
        "expected_passage_id": "kb:supplement_literature",
    },
    {
        "id": "HARD_LIT_004",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "comparative",
        "question": "Dòng văn học hiện thực phê phán 1930 - 1945 của Nam Cao và Ngô Tất Tố có điểm chung sâu sắc nào về giá trị nhân đạo?",
        "reference_answer": "Cả hai tác giả đều phản ánh chân thực số phận cùng khổ của người nông dân dưới ách áp bức phong kiến và thể hiện tấm lòng nhân đạo cao cả cùng niềm tin vào phẩm giá lương thiện của con người.",
        "expected_passage_id": "kb:deep_literature_culture",
    },
    {
        "id": "HARD_LIT_005",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "multi_hop",
        "question": "Ai là tác giả của áng thiên cổ hùng văn Bình Ngô đại cáo và tác phẩm được công bố sau thắng lợi của cuộc khởi nghĩa nào?",
        "reference_answer": "Đại thi hào danh nhân văn hóa Nguyễn Trãi thay lời Lê Lợi viết Bình Ngô đại cáo năm 1428 sau khi cuộc khởi nghĩa Lam Sơn toàn thắng đuổi sạch giặc Minh.",
        "expected_passage_id": "kb:supplement_history",
    },
    {
        "id": "HARD_LIT_006",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "cause_and_effect",
        "question": "Tại sao bài thơ Nam quốc sơn hà tương truyền do Lý Thường Kiệt đọc năm 1077 được coi là bản Tuyên ngôn Độc lập đầu tiên của nước ta?",
        "reference_answer": "Vì bài thơ đã khẳng định đanh thép chủ quyền lãnh thổ thiêng liêng của dân tộc Đại Việt được ghi rõ tại sách trời và cảnh cáo kẻ thù xâm phạm sẽ chuốc lấy bại vong.",
        "expected_passage_id": "kb:supplement_history",
    },
    {
        "id": "HARD_LIT_007",
        "category": "Văn học & Văn hóa",
        "reasoning_type": "technical_depth",
        "question": "Nguyễn Du đã sáng tạo cải biến tác phẩm Kim Vân Kiều truyện của Thanh Tâm Tài Nhân thành kiệt tác Truyện Kiều ở những phương diện nghệ thuật cốt lõi nào?",
        "reference_answer": "Nguyễn Du chuyển thể từ tiểu thuyết văn xuôi Trung Quốc sang 3.254 câu thơ lục bát chữ Nôm tuyệt diệu, thấm đẫm cảm hứng nhân đạo xót thương thân phận con người và miêu tả tâm lý nội tâm nhân vật bậc thầy.",
        "expected_passage_id": "kb:deep_literature_culture",
    },

    # --- Category 5: Công nghệ & Hệ thống Voice AI (Kiến trúc & Tối ưu hóa) ---
    {
        "id": "HARD_TECH_001",
        "category": "Công nghệ & AI",
        "reasoning_type": "technical_depth",
        "question": "Mô hình nhận dạng giọng nói Whisper-small trong hệ thống ViMMRC được tối ưu hóa bằng những kỹ thuật gì để chạy nhanh gấp 4 lần trên CPU?",
        "reference_answer": "Whisper-small được fine-tune bằng phương pháp thích ứng tham số LoRA 50 giờ, sau đó merge trọng số và chuyển đổi sang định dạng CTranslate2 với lượng tử hóa INT8 (INT8 quantization).",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_002",
        "category": "Công nghệ & AI",
        "reasoning_type": "comparative",
        "question": "So sánh vai trò và cơ chế truy xuất giữa tầng tri thức 1 (KB) và tầng tri thức 2 (Wikipedia) trong hệ thống RAG 2 tầng?",
        "reference_answer": "Tầng KB (5.879 đoạn) dùng BM25s tối ưu cho các bài đọc miền đóng; tầng Wikipedia (1.48 triệu đoạn) kết hợp sharded BM25s và vector embedding e5-small 384 chiều cho câu hỏi miền mở, xếp hạng chung bằng Cross-Encoder bge-reranker-v2-m3.",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_003",
        "category": "Công nghệ & AI",
        "reasoning_type": "technical_depth",
        "question": "Mô hình đọc hiểu ViT5-base có bao nhiêu tham số, được huấn luyện trên bao nhiêu câu hỏi và đạt độ chính xác kiểm thử bao nhiêu?",
        "reference_answer": "ViT5-base có 220 triệu tham số, được fine-tune trên 27.164 câu hỏi kết hợp ViMMRC và ViQuAD 2.0, đạt Exact Match 41.05% và token F1 66.55% trên tập kiểm thử.",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_004",
        "category": "Công nghệ & AI",
        "reasoning_type": "technical_depth",
        "question": "Công nghệ tổng hợp tiếng nói Matcha-TTS sử dụng kiến trúc âm học gì và kết hợp với bộ giải mã nào để tạo sóng âm tần số 22.050 Hz?",
        "reference_answer": "Matcha-TTS sử dụng kiến trúc Optimal Transport Conditional Flow Matching (OT-CFM) kết hợp với bộ giải mã âm học HiFi-GAN sinh dạng sóng âm thanh tần số 22.050 Hz tự nhiên.",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_005",
        "category": "Công nghệ & AI",
        "reasoning_type": "cause_and_effect",
        "question": "Tại sao việc áp dụng chiến lược ngữ cảnh question_chunks lại giúp ViT5 sinh ra câu trả lời chính xác hơn trên các bài đọc văn bản dài?",
        "reference_answer": "Vì question_chunks trích chọn đúng các phân đoạn mang bằng chứng liên quan trực tiếp đến câu hỏi, ngăn ngừa hiện tượng cắt cụt đầu văn bản (head truncation) khi văn bản dài hơn độ dài tối đa 512 token.",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_006",
        "category": "Công nghệ & AI",
        "reasoning_type": "comparative",
        "question": "Phân tích sự khác biệt về độ trễ xử lý trên CPU 4 luồng khi hệ thống bật và tắt mô hình Cross-Encoder reranker?",
        "reference_answer": "Khi bật reranker bge-reranker-v2-m3 độ trễ truy xuất khoảng ~6s (tổng chuỗi ~12s) với độ chính xác cao nhất; khi tắt reranker độ trễ truy xuất chỉ còn ~0.5s (tổng chuỗi ~5-6s).",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
    {
        "id": "HARD_TECH_007",
        "category": "Công nghệ & AI",
        "reasoning_type": "technical_depth",
        "question": "Kỹ thuật Contextual Query Reformulation trong phân hệ đối thoại giúp giải quyết thách thức cốt lõi nào trong hội thoại dài nhiều lượt?",
        "reference_answer": "Kỹ thuật này phát hiện các đại từ chỉ định hoặc nhân xưng (ông ấy, nơi đó, mô hình này) và tự động bổ sung thực thể chủ đề từ các lượt trước vào câu truy vấn để BM25 và Reranker tìm đúng bài viết.",
        "expected_passage_id": "kb:deep_voice_ai_architecture",
    },
]

MULTITURN_SCENARIOS = [
    {
        "scenario_id": "SCENARIO_01_HISTORY_QUANGTRUNG",
        "title": "Hội Thoại Chuyên Sâu Lịch Sử: Thiên Tài Quân Sự Quang Trung - Nguyễn Huệ",
        "domain": "Lịch sử Việt Nam",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "question": "Xin chào bạn, hôm nay tôi muốn cùng bạn tìm hiểu chuyên sâu về vua Quang Trung.",
                "expected_intent": "greeting",
                "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
            },
            {
                "turn": 2,
                "role": "user",
                "question": "Vua Quang Trung tên thật là gì và ông đã chỉ huy chiến dịch đại phá đội quân xâm lược nào vào năm 1789?",
                "expected_topic": "Vua Quang Trung",
                "reference_answer": "Vua Quang Trung tên thật là Nguyễn Huệ, đã chỉ huy chiến dịch đại phá 29 vạn quân Mãn Thanh xâm lược do Tôn Sĩ Nghị cầm đầu vào mùa xuân năm Kỷ Dậu 1789.",
            },
            {
                "turn": 3,
                "role": "user",
                "question": "Chiến thuật hành quân thần tốc của ông ấy từ Phú Xuân ra Thăng Long được tổ chức với điểm gì đặc biệt?",
                "requires_reformulation": True,
                "reference_answer": "Vua Quang Trung tổ chức chia quân lính thành từng tốp ba người thay phiên nhau gánh cáng một người nghỉ ngơi luân phiên ngày đêm, đồng thời dừng chân tuyển mộ thêm hàng vạn binh sĩ tinh nhuệ tại Nghệ An và Thanh Hóa.",
            },
            {
                "turn": 4,
                "role": "user",
                "question": "Trận đánh then chốt nào đã khiến tướng giặc Sầm Nghi Đống khiếp sợ thắt cổ tự tử?",
                "requires_reformulation": True,
                "reference_answer": "Trận then chốt Khương Thượng Đống Đa do Đô đốc Đặng Tiến Đông chỉ huy phối hợp cùng nhân dân dùng rồng lửa uy hiếp đã khiến thái thú Điền Châu Sầm Nghi Đống khiếp sợ thắt cổ tự tử trên núi Loa.",
            },
            {
                "turn": 5,
                "role": "user",
                "question": "Ý nghĩa lịch sử to lớn nhất của chiến thắng Ngọc Hồi Đống Đa này là gì?",
                "requires_reformulation": True,
                "reference_answer": "Chiến thắng Ngọc Hồi Đống Đa năm 1789 đã giải phóng hoàn toàn kinh thành Thăng Long, bảo vệ vững chắc độc lập chủ quyền Đại Việt và đập tan hoàn toàn dã tâm bành trướng của nhà Mãn Thanh.",
            },
            {
                "turn": 6,
                "role": "user",
                "question": "Sau khi lên ngôi, ông đã ban hành chính sách cải cách văn hóa giáo dục nào đáng chú ý?",
                "requires_reformulation": True,
                "reference_answer": "Vua Quang Trung ban hành Chiếu khuyến học, thành lập Viện Sùng chính do La Sơn Phu Tử Nguyễn Thiếp đứng đầu nhằm dịch sách chữ Hán sang chữ Nôm và đề cao chữ Nôm thành văn tự quốc gia trong chiếu thư hành chính và thi cử.",
            },
            {
                "turn": 7,
                "role": "user",
                "question": "Bạn trả lời rất xuất sắc và chi tiết, cảm ơn bạn rất nhiều nhé!",
                "expected_intent": "gratitude",
                "reference_answer": "Rất vui được hỗ trợ bạn tìm hiểu chi tiết về Vua Quang Trung! Nếu bạn còn bất kỳ câu hỏi nào khác, hãy cứ hỏi tôi nhé.",
            },
            {
                "turn": 8,
                "role": "user",
                "question": "Tạm biệt bạn nhé.",
                "expected_intent": "farewell",
                "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
            },
        ],
    },
    {
        "scenario_id": "SCENARIO_02_VOICE_AI_ARCHITECTURE",
        "title": "Hội Thoại Chuyên Sâu Công Nghệ: Kiến Trúc Hệ Thống Voice AI ViMMRC",
        "domain": "Công nghệ & AI",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "question": "Chào bạn, hãy giới thiệu cho tôi biết kiến trúc tổng thể của hệ thống ViMMRC Voice Q&A gồm những phân hệ nào?",
                "expected_topic": "Hệ thống ViMMRC",
                "reference_answer": "Hệ thống ViMMRC Voice Q&A tích hợp 4 phân hệ chính: Nhận dạng giọng nói (STT Whisper LoRA INT8), Truy xuất tri thức (Retrieval RAG 2 tầng), Đọc hiểu văn bản (MRC ViT5) và Tổng hợp tiếng nói (TTS Matcha/Edge).",
            },
            {
                "turn": 2,
                "role": "user",
                "question": "Phân hệ STT sử dụng mô hình nền tảng nào và được tối ưu hóa ra sao để chạy nhanh trên CPU?",
                "requires_reformulation": True,
                "reference_answer": "Phân hệ STT ứng dụng mô hình OpenAI Whisper-small tinh chỉnh bằng LoRA trên 50 giờ dữ liệu tiếng Việt, sau đó chuyển đổi sang CTranslate2 với lượng tử hóa INT8 giúp tăng tốc 4 lần trên CPU đạt WER 8.1%.",
            },
            {
                "turn": 3,
                "role": "user",
                "question": "Sau khi nhận dạng giọng nói xong, văn bản được đưa qua cơ chế truy xuất RAG 2 tầng như thế nào?",
                "requires_reformulation": True,
                "reference_answer": "RAG tầng 1 dùng 5.879 đoạn văn KB tối ưu BM25s cho miền đóng; tầng 2 dùng 1.48 triệu đoạn Wikipedia sharded BM25s kết hợp embedding đa ngữ e5-small 384 chiều, xếp hạng chung qua Cross-Encoder bge-reranker-v2-m3.",
            },
            {
                "turn": 4,
                "role": "user",
                "question": "Mô hình đọc hiểu ViT5 trong phân hệ MRC đạt kết quả đánh giá bao nhiêu trên tập kiểm thử?",
                "requires_reformulation": True,
                "reference_answer": "Mô hình ViT5-base 220 triệu tham số fine-tune trên 27.164 câu hỏi đạt Exact Match 41.05% và token F1 66.55% trên tập kiểm thử.",
            },
            {
                "turn": 5,
                "role": "user",
                "question": "Phân hệ TTS áp dụng công nghệ gì để đọc câu trả lời bằng giọng nói tự nhiên?",
                "requires_reformulation": True,
                "reference_answer": "Phân hệ TTS tích hợp công nghệ Matcha-TTS kiến trúc Optimal Transport Conditional Flow Matching (OT-CFM) kết hợp vocoder HiFi-GAN sinh âm thanh 22.050 Hz tự nhiên, cùng Edge-TTS và fallback gTTS.",
            },
            {
                "turn": 6,
                "role": "user",
                "question": "Độ trễ toàn chuỗi trên CPU 4 luồng là bao nhiêu và hệ thống có hỗ trợ triển khai bằng Docker không?",
                "requires_reformulation": True,
                "reference_answer": "Độ trễ toàn chuỗi trên CPU 4 luồng Docker khoảng ~12 giây (STT ~3s, RAG ~6s, ViT5 ~1.4s, TTS ~1.3s; tắt reranker còn ~5-6s) và được đóng gói hoàn chỉnh bằng Docker và Docker Compose.",
            },
            {
                "turn": 7,
                "role": "user",
                "question": "Bạn giải thích kiến trúc rất rõ ràng, cảm ơn trợ lý nhiều!",
                "expected_intent": "gratitude",
                "reference_answer": "Rất vui được hỗ trợ bạn tìm hiểu chi tiết về Hệ thống ViMMRC! Nếu bạn còn bất kỳ câu hỏi nào khác, hãy cứ hỏi tôi nhé.",
            },
            {
                "turn": 8,
                "role": "user",
                "question": "Hẹn gặp lại bạn lần sau.",
                "expected_intent": "farewell",
                "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
            },
        ],
    },
    {
        "scenario_id": "SCENARIO_03_GEOGRAPHY_WONDERS",
        "title": "Hội Thoại Chuyên Sâu Địa Lý: Nóc Nhà Đông Dương Fansipan & Kỳ Quan Hang Sơn Đoòng",
        "domain": "Địa lý Việt Nam",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "question": "Xin chào trợ lý, tôi muốn tìm hiểu về các đỉnh núi và hang động kỳ vĩ nhất của Việt Nam.",
                "expected_intent": "greeting",
                "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
            },
            {
                "turn": 2,
                "role": "user",
                "question": "Đỉnh núi nào cao nhất Việt Nam, được mệnh danh là Nóc nhà Đông Dương và cao bao nhiêu mét?",
                "expected_topic": "Đỉnh Fansipan",
                "reference_answer": "Đỉnh Fansipan (Phan Xi Păng) cao chính xác 3.143 mét thuộc dãy Hoàng Liên Sơn tỉnh Lào Cai là ngọn núi cao nhất Việt Nam và Đông Dương.",
            },
            {
                "turn": 3,
                "role": "user",
                "question": "Hang động tự nhiên lớn nhất thế giới nằm ở tỉnh nào của nước ta và tên là gì?",
                "expected_topic": "Hang Sơn Đoòng",
                "reference_answer": "Hang Sơn Đoòng thuộc Vườn quốc gia Phong Nha - Kẻ Bàng huyện Bố Trạch tỉnh Quảng Bình là hang động tự nhiên lớn nhất thế giới.",
            },
            {
                "turn": 4,
                "role": "user",
                "question": "Hang động này được phát hiện vào năm nào và kích thước thể tích khổng lồ đến mức nào?",
                "requires_reformulation": True,
                "reference_answer": "Hang được phát hiện lần đầu năm 1991 bởi Hồ Khanh, khảo sát năm 2009 với chiều dài gần 9 km, vòm hang cao 200 m, rộng 150 m và thể tích 38.5 triệu mét khối.",
            },
            {
                "turn": 5,
                "role": "user",
                "question": "Bên trong hang động này có hệ sinh thái rừng nhiệt đới đặc biệt tên là gì?",
                "requires_reformulation": True,
                "reference_answer": "Bên trong hang Sơn Đoòng dưới hai hố sụt khổng lồ có khu rừng nhiệt đới nguyên sinh độc nhất vô nhị mang tên Vườn Địa Đàng (Garden of Edam).",
            },
            {
                "turn": 6,
                "role": "user",
                "question": "Những thông tin địa lý này rất thú vị và chi tiết, cảm ơn bạn!",
                "expected_intent": "gratitude",
                "reference_answer": "Rất vui được hỗ trợ bạn tìm hiểu chi tiết về Hang Sơn Đoòng! Nếu bạn còn bất kỳ câu hỏi nào khác, hãy cứ hỏi tôi nhé.",
            },
            {
                "turn": 7,
                "role": "user",
                "question": "Tạm biệt bạn nhé.",
                "expected_intent": "farewell",
                "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
            },
        ],
    },
    {
        "scenario_id": "SCENARIO_04_SCIENCE_BIOLOGY",
        "title": "Hội Thoại Chuyên Sâu Sinh Học: Quá Trình Quang Hợp & Hô Hấp Ở Thực Vật",
        "domain": "Khoa học & Đời sống",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "question": "Chào trợ lý ảo, tôi muốn hỏi về cách cây xanh tổng hợp năng lượng và hô hấp.",
                "expected_intent": "greeting",
                "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
            },
            {
                "turn": 2,
                "role": "user",
                "question": "Quá trình quang hợp của thực vật diễn ra trong bào quan nào và hấp thụ năng lượng nhờ sắc tố gì?",
                "expected_topic": "Quá trình quang hợp",
                "reference_answer": "Quá trình quang hợp diễn ra trong các bào quan lục lạp (chloroplast) của tế bào thực vật nhờ năng lượng ánh sáng được hấp thụ bởi sắc tố diệp lục (chlorophyll).",
            },
            {
                "turn": 3,
                "role": "user",
                "question": "Phương trình hóa học tổng quát và các sản phẩm tạo thành của quá trình này là gì?",
                "requires_reformulation": True,
                "reference_answer": "Phương trình tổng quát là 6CO2 + 6H2O -> C6H12O6 + 6O2, sản phẩm tạo thành là đường glucose và khí oxy giải phóng vào khí quyển.",
            },
            {
                "turn": 4,
                "role": "user",
                "question": "Vào ban đêm khi không có ánh sáng thì quá trình này thay đổi ra sao trong tế bào cây?",
                "requires_reformulation": True,
                "reference_answer": "Ban đêm quang hợp ngừng lại hoàn toàn, cây xanh thực hiện hô hấp tế bào trong ty thể hấp thụ oxy và thải ra khí carbon dioxide.",
            },
            {
                "turn": 5,
                "role": "user",
                "question": "Tại sao trong phòng ngủ kín lại không nên đặt quá nhiều chậu cây xanh vào ban đêm?",
                "requires_reformulation": True,
                "reference_answer": "Vì ban đêm cây xanh hô hấp hút khí oxy và thải ra khí carbon dioxide, nếu để nhiều cây trong phòng kín sẽ gây nguy cơ tranh chấp oxy và ngột ngạt cho con người.",
            },
            {
                "turn": 6,
                "role": "user",
                "question": "Cảm ơn bạn nhé, kiến thức sinh học này rất thực tế và bổ ích!",
                "expected_intent": "gratitude",
                "reference_answer": "Rất vui được hỗ trợ bạn tìm hiểu chi tiết về Quá trình quang hợp! Nếu bạn còn bất kỳ câu hỏi nào khác, hãy cứ hỏi tôi nhé.",
            },
            {
                "turn": 7,
                "role": "user",
                "question": "Tạm biệt bạn, chúc một ngày tốt lành.",
                "expected_intent": "farewell",
                "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
            },
        ],
    },
]


def main():
    payload = {
        "metadata": {
            "title": "ViMMRC Hard Questions and Multi-Turn Long Dialogue Benchmark Suite",
            "total_hard_questions": len(HARD_QUESTIONS),
            "total_multiturn_scenarios": len(MULTITURN_SCENARIOS),
            "total_dialogue_turns": sum(len(s["turns"]) for s in MULTITURN_SCENARIOS),
            "description": "Challenging multi-hop, comparative, cause-and-effect questions and extended multi-turn conversational scenarios with context & coreference resolution.",
        },
        "hard_questions": HARD_QUESTIONS,
        "multiturn_scenarios": MULTITURN_SCENARIOS,
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Generated {OUT_FILE} successfully!")
    print(f" - Hard Questions: {len(HARD_QUESTIONS)} items")
    print(f" - Multi-Turn Scenarios: {len(MULTITURN_SCENARIOS)} scenarios ({sum(len(s['turns']) for s in MULTITURN_SCENARIOS)} dialogue turns)")


if __name__ == "__main__":
    main()
