"""Build and validate an Out-of-Dataset Benchmark Suite (>100 items) for ViMMRC Voice Q&A.

Covers:
1. Conversational & Assistant Interactive Dialogues (25 items)
2. Vietnamese History & Figures (20 items)
3. Vietnamese Geography & Landmarks (20 items)
4. Vietnamese Literature, Culture & Traditions (15 items)
5. Science, Mathematics & Everyday Life (15 items)
6. Technology, AI & Speech Systems (15 items)
Total = 110 items.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

ITEMS = [
    # --- Category 1: Conversational & Assistant Interactive Dialogues (25 items) ---
    {
        "id": "OOD_CONV_001",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Xin chào bạn!",
        "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
    },
    {
        "id": "OOD_CONV_002",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Chào buổi sáng trợ lý ảo.",
        "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
    },
    {
        "id": "OOD_CONV_003",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Chào bạn, hôm nay thế nào?",
        "reference_answer": "Cảm ơn bạn đã quan tâm! Tôi là trợ lý AI nên luôn sẵn sàng 100% năng lượng để lắng nghe và giải đáp mọi câu hỏi của bạn.",
    },
    {
        "id": "OOD_CONV_004",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bạn là ai vậy?",
        "reference_answer": "Tôi là trợ lý hỏi đáp thông minh tiếng Việt ViMMRC Voice Q&A, kết hợp mô hình nhận dạng giọng nói Whisper, hệ thống truy xuất tri thức RAG, mô hình đọc hiểu ViT5 và công nghệ giọng đọc tự nhiên Matcha-TTS.",
    },
    {
        "id": "OOD_CONV_005",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Tên của bạn là gì?",
        "reference_answer": "Tôi là trợ lý hỏi đáp thông minh tiếng Việt ViMMRC Voice Q&A, kết hợp mô hình nhận dạng giọng nói Whisper, hệ thống truy xuất tri thức RAG, mô hình đọc hiểu ViT5 và công nghệ giọng đọc tự nhiên Matcha-TTS.",
    },
    {
        "id": "OOD_CONV_006",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Hãy giới thiệu về bản thân bạn.",
        "reference_answer": "Tôi là trợ lý hỏi đáp thông minh tiếng Việt ViMMRC Voice Q&A, kết hợp mô hình nhận dạng giọng nói Whisper, hệ thống truy xuất tri thức RAG, mô hình đọc hiểu ViT5 và công nghệ giọng đọc tự nhiên Matcha-TTS.",
    },
    {
        "id": "OOD_CONV_007",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Ai đã phát triển ra bạn?",
        "reference_answer": "Tôi là trợ lý hỏi đáp thông minh tiếng Việt ViMMRC Voice Q&A, kết hợp mô hình nhận dạng giọng nói Whisper, hệ thống truy xuất tri thức RAG, mô hình đọc hiểu ViT5 và công nghệ giọng đọc tự nhiên Matcha-TTS.",
    },
    {
        "id": "OOD_CONV_008",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bạn có thể làm được những gì?",
        "reference_answer": "Tôi có thể lắng nghe câu hỏi qua micro bằng giọng nói, tự động tra cứu tài liệu trong kho tri thức tiếng Việt, suy luận câu trả lời chính xác bằng mô hình ViT5 và đọc câu trả lời trực tiếp cho bạn bằng âm thanh tự nhiên.",
    },
    {
        "id": "OOD_CONV_009",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bạn giúp được gì cho tôi?",
        "reference_answer": "Tôi có thể lắng nghe câu hỏi qua micro bằng giọng nói, tự động tra cứu tài liệu trong kho tri thức tiếng Việt, suy luận câu trả lời chính xác bằng mô hình ViT5 và đọc câu trả lời trực tiếp cho bạn bằng âm thanh tự nhiên.",
    },
    {
        "id": "OOD_CONV_010",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Hướng dẫn sử dụng hệ thống này giúp tôi.",
        "reference_answer": "Tôi có thể lắng nghe câu hỏi qua micro bằng giọng nói, tự động tra cứu tài liệu trong kho tri thức tiếng Việt, suy luận câu trả lời chính xác bằng mô hình ViT5 và đọc câu trả lời trực tiếp cho bạn bằng âm thanh tự nhiên.",
    },
    {
        "id": "OOD_CONV_011",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Cảm ơn bạn nhé!",
        "reference_answer": "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, hãy cứ hỏi tôi nhé.",
    },
    {
        "id": "OOD_CONV_012",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Cảm ơn trợ lý nhiều.",
        "reference_answer": "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, hãy cứ hỏi tôi nhé.",
    },
    {
        "id": "OOD_CONV_013",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bạn trả lời thông minh quá!",
        "reference_answer": "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, hãy cứ hỏi tôi nhé.",
    },
    {
        "id": "OOD_CONV_014",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Tạm biệt bạn nhé.",
        "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
    },
    {
        "id": "OOD_CONV_015",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Hẹn gặp lại bạn lần sau.",
        "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
    },
    {
        "id": "OOD_CONV_016",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Chúc bạn ngủ ngon.",
        "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
    },
    {
        "id": "OOD_CONV_017",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Dạo này bạn khỏe không?",
        "reference_answer": "Cảm ơn bạn đã quan tâm! Tôi là trợ lý AI nên luôn sẵn sàng 100% năng lượng để lắng nghe và giải đáp mọi câu hỏi của bạn.",
    },
    {
        "id": "OOD_CONV_018",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Hello ViMMRC assistant",
        "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
    },
    {
        "id": "OOD_CONV_019",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Thank you very much",
        "reference_answer": "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, hãy cứ hỏi tôi nhé.",
    },
    {
        "id": "OOD_CONV_020",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bye bye trợ lý",
        "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
    },
    {
        "id": "OOD_CONV_021",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Chào anh bạn",
        "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
    },
    {
        "id": "OOD_CONV_022",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Chào buổi tối",
        "reference_answer": "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. Tôi có thể giúp gì cho bạn hôm nay?",
    },
    {
        "id": "OOD_CONV_023",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Tính năng của bạn gồm những gì?",
        "reference_answer": "Tôi có thể lắng nghe câu hỏi qua micro bằng giọng nói, tự động tra cứu tài liệu trong kho tri thức tiếng Việt, suy luận câu trả lời chính xác bằng mô hình ViT5 và đọc câu trả lời trực tiếp cho bạn bằng âm thanh tự nhiên.",
    },
    {
        "id": "OOD_CONV_024",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Bạn giỏi thật đấy",
        "reference_answer": "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, hãy cứ hỏi tôi nhé.",
    },
    {
        "id": "OOD_CONV_025",
        "category": "Hội thoại giao tiếp",
        "type": "conversation",
        "question": "Tạm biệt",
        "reference_answer": "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. Hẹn gặp lại bạn lần sau!",
    },

    # --- Category 2: Vietnamese History & Figures (20 items) ---
    {
        "id": "OOD_HIST_001",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Quang Trung đại phá quân Thanh vào năm nào?",
        "reference_answer": "Vua Quang Trung đại phá hai mươi chín vạn quân Thanh vào mùa xuân năm Kỷ Dậu 1789.",
    },
    {
        "id": "OOD_HIST_002",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Ai là người chỉ huy chiến thắng Bạch Đằng năm 938 chấm dứt nghìn năm Bắc thuộc?",
        "reference_answer": "Ngô Quyền là vị anh hùng dân tộc chỉ huy chiến thắng Bạch Đằng lịch sử năm 938.",
    },
    {
        "id": "OOD_HIST_003",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Hưng Đạo Đại Vương Trần Quốc Tuấn ba lần lãnh đạo nhân dân đánh tan quân xâm lược nào?",
        "reference_answer": "Trần Hưng Đạo đã lãnh đạo quân dân Đại Việt ba lần chiến thắng oanh liệt quân xâm lược Mông Nguyên.",
    },
    {
        "id": "OOD_HIST_004",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Hai Bà Trưng phất cờ khởi nghĩa chống lại ách đô hộ của phong kiến phương Bắc vào năm nào?",
        "reference_answer": "Hai Bà Trưng khởi nghĩa vào năm 40 sau Công Nguyên.",
    },
    {
        "id": "OOD_HIST_005",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Ai là tác giả của bản Tuyên ngôn Độc lập đầu tiên của nước ta mang tên Nam quốc sơn hà?",
        "reference_answer": "Bài thơ Nam quốc sơn hà tương truyền do danh tướng Lý Thường Kiệt đọc bên phòng tuyến sông Như Nguyệt năm 1077.",
    },
    {
        "id": "OOD_HIST_006",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Vị vua nào có công dẹp loạn 12 sứ quân và lập ra nhà nước Đại Cồ Việt?",
        "reference_answer": "Đinh Bộ Lĩnh tức vua Đinh Tiên Hoàng là người có công dẹp loạn mười hai sứ quân.",
    },
    {
        "id": "OOD_HIST_007",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Chủ tịch Hồ Chí Minh đọc bản Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa vào ngày tháng năm nào?",
        "reference_answer": "Chủ tịch Hồ Chí Minh đọc bản Tuyên ngôn Độc lập vào ngày 2 tháng 9 năm 1945 tại Quảng trường Ba Đình Hà Nội.",
    },
    {
        "id": "OOD_HIST_008",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Chiến dịch Điện Biên Phủ toàn thắng vào ngày tháng năm nào?",
        "reference_answer": "Chiến dịch Điện Biên Phủ toàn thắng vào ngày 7 tháng 5 năm 1954.",
    },
    {
        "id": "OOD_HIST_009",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Người anh hùng áo vải lãnh đạo cuộc khởi nghĩa Lam Sơn giành lại độc lập là ai?",
        "reference_answer": "Lê Lợi là người khởi xướng và lãnh đạo cuộc khởi nghĩa Lam Sơn chống giặc Minh.",
    },
    {
        "id": "OOD_HIST_010",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Kinh đô đầu tiên của nhà nước Văn Lang thời các vua Hùng nằm ở đâu?",
        "reference_answer": "Kinh đô của nhà nước Văn Lang đóng tại Phong Châu thuộc tỉnh Phú Thọ ngày nay.",
    },
    {
        "id": "OOD_HIST_011",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Vua Lý Thái Tổ ban Chiếu dời đô từ Hoa Lư về Thăng Long vào năm nào?",
        "reference_answer": "Vua Lý Thái Tổ ban Chiếu dời đô về Thăng Long vào năm 1010.",
    },
    {
        "id": "OOD_HIST_012",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Chiến dịch Hồ Chí Minh lịch sử giải phóng hoàn toàn miền Nam thống nhất đất nước toàn thắng vào ngày nào?",
        "reference_answer": "Chiến dịch Hồ Chí Minh toàn thắng vào trưa ngày 30 tháng 4 năm 1975.",
    },
    {
        "id": "OOD_HIST_013",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Đại tướng đầu tiên và Tổng tư lệnh Quân đội Nhân dân Việt Nam là ai?",
        "reference_answer": "Đại tướng Võ Nguyên Giáp là Đại tướng đầu tiên của Quân đội Nhân dân Việt Nam.",
    },
    {
        "id": "OOD_HIST_014",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Ai là người anh hùng thiếu niên bóp nát quả cam vì không được dự bàn việc nước đánh giặc Nguyên Mông?",
        "reference_answer": "Người anh hùng thiếu niên đó là Trần Quốc Toản.",
    },
    {
        "id": "OOD_HIST_015",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Ai là tác giả của bản thiên cổ hùng văn Bình Ngô đại cáo?",
        "reference_answer": "Danh nhân văn hóa thế giới Nguyễn Trãi là tác giả của Bình Ngô đại cáo.",
    },
    {
        "id": "OOD_HIST_016",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Trận Như Nguyệt năm 1077 diễn ra trên dòng sông nào ngày nay?",
        "reference_answer": "Sông Như Nguyệt chính là một đoạn của sông Cầu ngày nay.",
    },
    {
        "id": "OOD_HIST_017",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Thành Cổ Loa được xây dựng dưới triều đại của vị vua nào?",
        "reference_answer": "Thành Cổ Loa được xây dựng dưới triều đại An Dương Vương Thục Phán nước Âu Lạc.",
    },
    {
        "id": "OOD_HIST_018",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Bác Hồ ra đi tìm đường cứu nước từ bến cảng nào vào ngày 5 tháng 6 năm 1911?",
        "reference_answer": "Người ra đi tìm đường cứu nước từ Bến cảng Nhà Rồng tại Sài Gòn.",
    },
    {
        "id": "OOD_HIST_019",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Vị trạng nguyên trẻ tuổi nhất trong lịch sử khoa bảng Việt Nam là ai?",
        "reference_answer": "Nguyễn Hiền đỗ Trạng nguyên năm 1247 khi mới 13 tuổi, là vị Trạng nguyên trẻ nhất nước ta.",
    },
    {
        "id": "OOD_HIST_020",
        "category": "Lịch sử Việt Nam",
        "type": "factual",
        "question": "Phong trào Cần Vương chống thực dân Pháp do vị vua yêu nước nào ban chiếu phát động?",
        "reference_answer": "Phong trào Cần Vương do vua Hàm Nghi ban chiếu phát động vào năm 1885.",
    },

    # --- Category 3: Vietnamese Geography & Landmarks (20 items) ---
    {
        "id": "OOD_GEO_001",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Thủ đô của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam là thành phố nào?",
        "reference_answer": "Thủ đô của Việt Nam là thành phố Hà Nội.",
    },
    {
        "id": "OOD_GEO_002",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Đỉnh núi cao nhất Việt Nam và được mệnh danh là nóc nhà Đông Dương là đỉnh núi nào?",
        "reference_answer": "Đỉnh Fansipan với độ cao 3.143 mét tại dãy Hoàng Liên Sơn tỉnh Lào Cai.",
    },
    {
        "id": "OOD_GEO_003",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Hang động tự nhiên lớn nhất thế giới nằm ở tỉnh nào của Việt Nam?",
        "reference_answer": "Hang Sơn Đoòng thuộc Vườn quốc gia Phong Nha Kẻ Bàng tỉnh Quảng Bình.",
    },
    {
        "id": "OOD_GEO_004",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Đảo nào có diện tích lớn nhất của Việt Nam?",
        "reference_answer": "Đảo Phú Quốc thuộc tỉnh Kiên Giang là hòn đảo lớn nhất Việt Nam.",
    },
    {
        "id": "OOD_GEO_005",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Vịnh Hạ Long được UNESCO công nhận là di sản thiên nhiên thế giới thuộc tỉnh nào?",
        "reference_answer": "Vịnh Hạ Long thuộc địa phận tỉnh Quảng Ninh.",
    },
    {
        "id": "OOD_GEO_006",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Cột cờ Lũng Cú điểm cực Bắc của Tổ quốc thuộc huyện nào của tỉnh Hà Giang?",
        "reference_answer": "Cột cờ Lũng Cú nằm tại huyện Đồng Văn tỉnh Hà Giang.",
    },
    {
        "id": "OOD_GEO_007",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Điểm cực Nam trên đất liền của Việt Nam thuộc địa phận tỉnh nào?",
        "reference_answer": "Điểm cực Nam trên đất liền thuộc Mũi Cà Mau tỉnh Cà Mau.",
    },
    {
        "id": "OOD_GEO_008",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Dòng sông nào dài nhất chảy hoàn toàn bên trong lãnh thổ Việt Nam?",
        "reference_answer": "Sông Đồng Nai là con sông dài nhất chảy hoàn toàn trong nội địa Việt Nam.",
    },
    {
        "id": "OOD_GEO_009",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Đồng bằng sông Cửu Long còn được gọi bằng tên quen thuộc nào?",
        "reference_answer": "Đồng bằng sông Cửu Long còn được gọi là Đồng bằng Nam Bộ hoặc miền Tây Nam Bộ.",
    },
    {
        "id": "OOD_GEO_010",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Hồ nước ngọt tự nhiên lớn nhất Việt Nam là hồ nào?",
        "reference_answer": "Hồ Ba Bể thuộc tỉnh Bắc Kạn là hồ nước ngọt tự nhiên lớn nhất nước ta.",
    },
    {
        "id": "OOD_GEO_011",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Quần đảo Hoàng Sa và Trường Sa thuộc chủ quyền thiêng liêng của quốc gia nào?",
        "reference_answer": "Quần đảo Hoàng Sa và Trường Sa là lãnh thổ chủ quyền thiêng liêng không thể tách rời của Việt Nam.",
    },
    {
        "id": "OOD_GEO_012",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Thác nước tự nhiên lớn nhất Đông Nam Á nằm giữa biên giới Việt Nam và Trung Quốc tên là gì?",
        "reference_answer": "Đó là thác Bản Giốc thuộc tỉnh Cao Bằng.",
    },
    {
        "id": "OOD_GEO_013",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Thành phố Đà Lạt thành phố ngàn hoa nằm trên cao nguyên nào?",
        "reference_answer": "Thành phố Đà Lạt nằm trên cao nguyên Lâm Viên tỉnh Lâm Đồng.",
    },
    {
        "id": "OOD_GEO_014",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Cố đô Huế với dòng sông Hương thơ mộng thuộc tỉnh nào?",
        "reference_answer": "Cố đô Huế thuộc tỉnh Thừa Thiên Huế miền Trung Việt Nam.",
    },
    {
        "id": "OOD_GEO_015",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Việt Nam có đường bờ biển dài khoảng bao nhiêu kilomet?",
        "reference_answer": "Việt Nam có đường bờ biển dài khoảng 3.260 kilomet trải dài từ Móng Cái đến Hà Tiên.",
    },
    {
        "id": "OOD_GEO_016",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Tỉnh nào ở Việt Nam có diện tích tự nhiên rộng nhất cả nước?",
        "reference_answer": "Nghệ An là tỉnh có diện tích tự nhiên lớn nhất Việt Nam.",
    },
    {
        "id": "OOD_GEO_017",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Tỉnh nào có diện tích đất tự nhiên nhỏ nhất nước ta?",
        "reference_answer": "Bắc Ninh là tỉnh có diện tích tự nhiên nhỏ nhất Việt Nam.",
    },
    {
        "id": "OOD_GEO_018",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Đèo Hải Vân là ranh giới tự nhiên giữa hai địa phương nào?",
        "reference_answer": "Đèo Hải Vân là ranh giới tự nhiên giữa tỉnh Thừa Thiên Huế và thành phố Đà Nẵng.",
    },
    {
        "id": "OOD_GEO_019",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Núi Bà Đen ngọn núi cao nhất miền Đông Nam Bộ thuộc tỉnh nào?",
        "reference_answer": "Núi Bà Đen với độ cao 986 mét thuộc tỉnh Tây Ninh.",
    },
    {
        "id": "OOD_GEO_020",
        "category": "Địa lý Việt Nam",
        "type": "factual",
        "question": "Sông Hồng bắt nguồn từ đâu trước khi chảy vào Việt Nam?",
        "reference_answer": "Sông Hồng bắt nguồn từ vùng núi tỉnh Vân Nam Trung Quốc.",
    },

    # --- Category 4: Vietnamese Literature, Culture & Traditions (15 items) ---
    {
        "id": "OOD_LIT_001",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Ai là tác giả của kiệt tác Truyện Kiều trong nền văn học cổ điển Việt Nam?",
        "reference_answer": "Đại thi hào Nguyễn Du là tác giả của kiệt tác Truyện Kiều.",
    },
    {
        "id": "OOD_LIT_002",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Truyện Kiều được viết theo thể thơ truyền thống nào của dân tộc?",
        "reference_answer": "Truyện Kiều được viết bằng thể thơ lục bát gồm 3.254 câu thơ.",
    },
    {
        "id": "OOD_LIT_003",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Nhà văn hiện thực Nam Cao nổi tiếng với tác phẩm về nhân vật nông dân nghèo nào nuôi chó vàng?",
        "reference_answer": "Đó là tác phẩm Lão Hạc với nhân vật trung tâm là lão Hạc và con chó Vàng.",
    },
    {
        "id": "OOD_LIT_004",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Sự tích Bánh chưng bánh giầy gắn liền với nhân vật hoàng tử nào thời vua Hùng thứ sáu?",
        "reference_answer": "Sự tích gắn liền với hoàng tử Lang Liêu.",
    },
    {
        "id": "OOD_LIT_005",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Nhạc cụ truyền thống độc đáo của Việt Nam chỉ có duy nhất một dây phát ra âm thanh tên là gì?",
        "reference_answer": "Đó là đàn bầu hay còn gọi là độc huyền cầm.",
    },
    {
        "id": "OOD_LIT_006",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Lễ hội Đền Hùng tưởng nhớ các vị vua lập nước được tổ chức vào ngày tháng âm lịch nào?",
        "reference_answer": "Lễ giỗ Tổ Hùng Vương được tổ chức vào ngày mùng 10 tháng 3 âm lịch hàng năm.",
    },
    {
        "id": "OOD_LIT_007",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Dòng tranh dân gian truyền thống in khắc gỗ trên giấy điệp nổi tiếng của làng nào ở Bắc Ninh?",
        "reference_answer": "Đó là dòng tranh dân gian Đông Hồ thuộc làng Đông Hồ tỉnh Bắc Ninh.",
    },
    {
        "id": "OOD_LIT_008",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Tác phẩm Dế Mèn phiêu lưu ký là kiệt tác văn học thiếu nhi của nhà văn nào?",
        "reference_answer": "Dế Mèn phiêu lưu ký là tác phẩm nổi tiếng của nhà văn Tô Hoài.",
    },
    {
        "id": "OOD_LIT_009",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Áo dài truyền thống của người phụ nữ Việt Nam thường được may bằng chất liệu vải gì đặc trưng?",
        "reference_answer": "Áo dài truyền thống thường được may bằng chất liệu lụa tơ tằm mềm mại.",
    },
    {
        "id": "OOD_LIT_010",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Tết Trung thu của người Việt Nam diễn ra vào ngày tháng âm lịch nào trong năm?",
        "reference_answer": "Tết Trung thu diễn ra vào ngày rằm tháng tám âm lịch tức ngày 15 tháng 8 âm lịch.",
    },
    {
        "id": "OOD_LIT_011",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Dân ca Quan họ là nét di sản văn hóa phi vật thể tiêu biểu của vùng quê nào?",
        "reference_answer": "Dân ca Quan họ là nét văn hóa đặc sắc của vùng Kinh Bắc gồm Bắc Ninh và Bắc Giang.",
    },
    {
        "id": "OOD_LIT_012",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Nhà thơ nào được mệnh danh là Bà chúa thơ Nôm trong nền thơ ca Việt Nam?",
        "reference_answer": "Nữ sĩ Hồ Xuân Hương được xưng tụng là Bà chúa thơ Nôm.",
    },
    {
        "id": "OOD_LIT_013",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Nghệ thuật Múa rối nước là loại hình nghệ thuật sân khấu dân gian bắt nguồn từ nền văn minh nào?",
        "reference_answer": "Múa rối nước bắt nguồn từ nền văn minh lúa nước vùng đồng bằng Bắc Bộ Việt Nam.",
    },
    {
        "id": "OOD_LIT_014",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Tác giả của bài thơ Tây Tiến hào hùng về người lính vệ quốc là ai?",
        "reference_answer": "Nhà thơ Quang Dũng là tác giả của bài thơ Tây Tiến.",
    },
    {
        "id": "OOD_LIT_015",
        "category": "Văn học & Văn hóa",
        "type": "factual",
        "question": "Không gian văn hóa Cồng chiêng Tây Nguyên đã được UNESCO công nhận là gì?",
        "reference_answer": "Không gian văn hóa Cồng chiêng Tây Nguyên là Kiệt tác truyền khẩu và Di sản văn hóa phi vật thể của nhân loại.",
    },

    # --- Category 5: Science, Mathematics & Everyday Life (15 items) ---
    {
        "id": "OOD_SCI_001",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Nước tinh khiết đóng băng ở bao nhiêu độ C trong điều kiện tiêu chuẩn?",
        "reference_answer": "Nước tinh khiết đóng băng ở 0 độ C.",
    },
    {
        "id": "OOD_SCI_002",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Nước sôi ở bao nhiêu độ C ở điều kiện áp suất khí quyển tiêu chuẩn 1 atm?",
        "reference_answer": "Nước sôi ở 100 độ C ở áp suất 1 atm.",
    },
    {
        "id": "OOD_SCI_003",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Hành tinh nào nằm ở vị trí gần Mặt Trời nhất trong Hệ Mặt Trời?",
        "reference_answer": "Sao Thủy là hành tinh gần Mặt Trời nhất trong Hệ Mặt Trời.",
    },
    {
        "id": "OOD_SCI_004",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Hành tinh lớn nhất trong Hệ Mặt Trời của chúng ta là hành tinh nào?",
        "reference_answer": "Sao Mộc là hành tinh có khối lượng và kích thước lớn nhất Hệ Mặt Trời.",
    },
    {
        "id": "OOD_SCI_005",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Vận tốc của ánh sáng truyền trong chân không xấp xỉ khoảng bao nhiêu kilomet trên giây?",
        "reference_answer": "Vận tốc ánh sáng trong chân không là khoảng 300.000 kilomet trên giây.",
    },
    {
        "id": "OOD_SCI_006",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Khí nào chiếm hàm lượng phần trăm thể tích lớn nhất trong bầu khí quyển Trái Đất?",
        "reference_answer": "Khí Nitơ chiếm khoảng 78 phần trăm thể tích bầu khí quyển Trái Đất.",
    },
    {
        "id": "OOD_SCI_007",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Công thức hóa học của nước gồm những nguyên tố nào?",
        "reference_answer": "Nước có công thức hóa học là H2O gồm 2 nguyên tử Hydro và 1 nguyên tử Oxy.",
    },
    {
        "id": "OOD_SCI_008",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Bộ xương người trưởng thành bình thường có khoảng bao nhiêu chiếc xương?",
        "reference_answer": "Cơ thể người trưởng thành có tổng cộng 206 chiếc xương.",
    },
    {
        "id": "OOD_SCI_009",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Một năm dương lịch thông thường có bao nhiêu ngày?",
        "reference_answer": "Một năm dương lịch bình thường có 365 ngày, năm nhuận có 366 ngày.",
    },
    {
        "id": "OOD_SCI_010",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Một ngày đêm trên Trái Đất có bao nhiêu giờ?",
        "reference_answer": "Một ngày đêm trên Trái Đất có 24 giờ tương đương 1.440 phút.",
    },
    {
        "id": "OOD_SCI_011",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Kim loại nào có khả năng dẫn điện và dẫn nhiệt tốt nhất trong tự nhiên?",
        "reference_answer": "Bạc là kim loại có độ dẫn điện và dẫn nhiệt tốt nhất.",
    },
    {
        "id": "OOD_SCI_012",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Trái Đất quay một vòng quanh trục của nó mất khoảng thời gian bao lâu?",
        "reference_answer": "Trái Đất quay một vòng quanh trục mất khoảng 24 giờ tức một ngày đêm.",
    },
    {
        "id": "OOD_SCI_013",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Quá trình quang hợp ở thực vật xanh tạo ra khí gì cần thiết cho sự sống của con người?",
        "reference_answer": "Quá trình quang hợp hấp thụ khí Cacbonic và giải phóng khí Oxy.",
    },
    {
        "id": "OOD_SCI_014",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Hình tam giác có tổng số đo ba góc trong bằng bao nhiêu độ?",
        "reference_answer": "Tổng số đo ba góc trong của một hình tam giác luôn bằng 180 độ.",
    },
    {
        "id": "OOD_SCI_015",
        "category": "Khoa học & Đời sống",
        "type": "factual",
        "question": "Nhịp tim trung bình của một người trưởng thành khỏe mạnh lúc nghỉ ngơi là bao nhiêu nhịp mỗi phút?",
        "reference_answer": "Nhịp tim người trưởng thành bình thường dao động từ 60 đến 100 nhịp mỗi phút.",
    },

    # --- Category 6: Technology, AI & Speech Systems (15 items) ---
    {
        "id": "OOD_TECH_001",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "AI là viết tắt của thuật ngữ gì trong công nghệ thông tin?",
        "reference_answer": "AI là viết tắt của cụm từ tiếng Anh Artificial Intelligence tức Trí tuệ nhân tạo.",
    },
    {
        "id": "OOD_TECH_002",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Công nghệ STT viết tắt từ cụm từ nào và có chức năng gì?",
        "reference_answer": "STT là viết tắt của Speech to Text, tức công nghệ chuyển đổi giọng nói thành văn bản.",
    },
    {
        "id": "OOD_TECH_003",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Công nghệ TTS là viết tắt của từ gì và có tác dụng như thế nào?",
        "reference_answer": "TTS là viết tắt của Text to Speech, tức công nghệ tổng hợp giọng nói từ văn bản.",
    },
    {
        "id": "OOD_TECH_004",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Mô hình Whisper của OpenAI được nhóm sử dụng cho phân hệ nào trong dự án ViMMRC?",
        "reference_answer": "Mô hình Whisper được sử dụng cho phân hệ nhận dạng giọng nói tiếng Việt Speech to Text.",
    },
    {
        "id": "OOD_TECH_005",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Mô hình ViT5 được sử dụng để thực hiện nhiệm vụ gì trong hệ thống hỏi đáp?",
        "reference_answer": "Mô hình ViT5 thực hiện nhiệm vụ đọc hiểu máy và sinh câu trả lời tự nhiên từ ngữ cảnh tài liệu.",
    },
    {
        "id": "OOD_TECH_006",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Matcha-TTS áp dụng kỹ thuật sinh âm thanh tiên tiến nào?",
        "reference_answer": "Matcha-TTS áp dụng kiến trúc Optimal Transport Conditional Flow Matching kết hợp bộ mã hóa HiFi-GAN.",
    },
    {
        "id": "OOD_TECH_007",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Phương pháp fine-tune LoRA là viết tắt của thuật ngữ gì?",
        "reference_answer": "LoRA là viết tắt của Low-Rank Adaptation, kỹ thuật tinh chỉnh tham số hiệu quả cho mô hình ngôn ngữ lớn.",
    },
    {
        "id": "OOD_TECH_008",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Định dạng âm thanh PCM 16kHz thường được dùng cho mục đích gì trong học máy tiếng nói?",
        "reference_answer": "Định dạng PCM 16kHz là chuẩn tần số lấy mẫu tối ưu cho các mô hình nhận dạng tiếng nói tự động.",
    },
    {
        "id": "OOD_TECH_009",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Thuật toán BM25 trong phân hệ Retrieval thuộc loại thuật toán truy xuất nào?",
        "reference_answer": "BM25 là thuật toán xếp hạng tài liệu dựa trên tần suất từ vựng và độ dài văn bản trong truy xuất thông tin.",
    },
    {
        "id": "OOD_TECH_010",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Mô hình Cross-Encoder reranker được dùng để làm gì trong chuỗi RAG?",
        "reference_answer": "Reranker chấm điểm tương quan ngữ nghĩa sâu sắc giữa câu hỏi và đoạn trích để sắp xếp lại độ ưu tiên.",
    },
    {
        "id": "OOD_TECH_011",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Thư viện CTranslate2 giúp ích gì cho mô hình Whisper?",
        "reference_answer": "CTranslate2 giúp tăng tốc suy luận và lượng tử hóa mô hình INT8, giảm độ trễ và tiêu thụ bộ nhớ RAM.",
    },
    {
        "id": "OOD_TECH_012",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Kiến trúc RAG trong xử lý ngôn ngữ tự nhiên là viết tắt của từ gì?",
        "reference_answer": "RAG là viết tắt của Retrieval Augmented Generation tức mô hình sinh có tăng cường truy xuất tri thức.",
    },
    {
        "id": "OOD_TECH_013",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Chỉ số WER trong đánh giá mô hình nhận dạng giọng nói là viết tắt của từ gì?",
        "reference_answer": "WER là viết tắt của Word Error Rate tức tỷ lệ từ sai sót trong nhận dạng tiếng nói.",
    },
    {
        "id": "OOD_TECH_014",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Chỉ số Exact Match trong đánh giá mô hình hỏi đáp đo lường điều gì?",
        "reference_answer": "Exact Match đo lường tỷ lệ phần trăm câu trả lời dự đoán trùng khớp tuyệt đối 100% với đáp án chuẩn.",
    },
    {
        "id": "OOD_TECH_015",
        "category": "Công nghệ & AI",
        "type": "factual",
        "question": "Docker container đem lại lợi ích gì cho việc triển khai hệ thống ViMMRC?",
        "reference_answer": "Docker giúp đóng gói nhất quán toàn bộ môi trường, thư viện và mô hình, cho phép triển khai chạy trên mọi hệ điều hành.",
    },
]


def verify_no_data_leakage(items: list[dict]) -> tuple[bool, int]:
    """Verify that none of the benchmark questions exist in train/dev/test datasets."""
    existing_questions = set()

    for split in ["train_vimmrc.json", "dev_vimmrc.json", "test_vimmrc.json"]:
        split_path = DATA_DIR / split
        if split_path.exists():
            records = json.loads(split_path.read_text(encoding="utf-8"))
            for r in records:
                for q in r.get("questions", []):
                    clean_q = q.strip().lower()
                    existing_questions.add(clean_q)

    overlap_count = 0
    for item in items:
        q_clean = item["question"].strip().lower()
        if q_clean in existing_questions:
            print(f"WARNING: Overlapping question found: {item['question']}")
            overlap_count += 1

    return (overlap_count == 0, overlap_count)


def main():
    print(f"Total benchmark items: {len(ITEMS)}")
    assert len(ITEMS) >= 100, f"Expected at least 100 items, got {len(ITEMS)}"

    no_leakage, count = verify_no_data_leakage(ITEMS)
    print(f"Data leakage check: {'PASSED (0 overlap)' if no_leakage else f'FAILED ({count} overlaps)'}")
    assert no_leakage, "Data leakage detected!"

    out_file = DATA_DIR / "out_of_dataset_eval_100.json"
    out_file.write_text(json.dumps(ITEMS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved benchmark suite to {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
