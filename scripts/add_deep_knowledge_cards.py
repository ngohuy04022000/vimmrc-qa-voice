"""Add deep, multi-topic, and multi-hop knowledge cards to data/kb_index.json."""
from __future__ import annotations

import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "kb_index.json"

DEEP_CARDS = [
    {
        "id": "kb:deep_history_quangtrung",
        "passage": (
            "Vua Quang Trung tên thật là Nguyễn Huệ (1753 - 1792), người anh hùng áo vải cờ đào kiệt xuất của phong trào khởi nghĩa nông dân Tây Sơn. "
            "Vào mùa xuân năm Kỷ Dậu 1789, vua Quang Trung đã chỉ huy chiến dịch đại phá 29 vạn quân Mãn Thanh xâm lược do Tổng đốc Lưỡng Quảng Tôn Sĩ Nghị cầm đầu. "
            "Nghệ thuật hành quân thần tốc của vua Quang Trung: Ngày 25 tháng 11 năm Mậu Thân (22 tháng 12 năm 1788), Nguyễn Huệ làm lễ lên ngôi Hoàng đế tại núi Bân (Huế) lấy niên hiệu Quang Trung rồi lập tức xuất quân ra Bắc. "
            "Trên đường hành quân, vua tổ chức chia quân lính thành từng tốp ba người, hai người thay phiên nhau gánh cáng một người nghỉ ngơi luân phiên ngày đêm, đồng thời dừng chân tuyển mộ thêm hàng vạn binh sĩ tinh nhuệ tại Nghệ An và Thanh Hóa. "
            "Chỉ trong vòng vài ngày, đội quân Tây Sơn đã vượt hơn 600 km tập kết tại phòng tuyến Tam Điệp - Biện Sơn (Ninh Bình). "
            "Tại đây, vua Quang Trung tổ chức cho ba quân ăn Tết Nguyên Đán sớm và tuyên bố hẹn mùng 7 Tết Kỷ Dậu sẽ vào thành Thăng Long mở tiệc khải hoàn mừng chiến thắng. "
            "Trận then chốt Ngọc Hồi diễn ra vào sáng sớm mùng 5 Tết Kỷ Dậu 1789: Đích thân vua Quang Trung cưỡi voi đốc chiến, chỉ đạo binh sĩ lấy các tấm ván rơm tẩm nước bọc ngoài chống đạn hỏa hổ xông lên phá tan đồn lũy Ngọc Hồi kiên cố nhất của địch. "
            "Trận then chốt Khương Thượng Đống Đa: Đạo quân tập kích bất ngờ do Đô đốc Đặng Tiến Đông chỉ huy đã phối hợp cùng nhân dân địa phương dùng rồng lửa tấn công dữ dội đồn Khương Thượng, khiến tướng giặc thái thú Điền Châu Sầm Nghi Đống khiếp đảm thắt cổ tự tử trên núi Loa (núi Ốc). "
            "Tôn Sĩ Nghị hoảng loạn không kịp mặc giáp vứt bỏ ấn tín cùng tàn quân chạy tháo thân qua cầu phao sông Hồng, binh lính chen lấn làm đứt cầu chết đuối vô số. "
            "Ý nghĩa lịch sử to lớn: Chiến thắng Ngọc Hồi Đống Đa năm 1789 đã giải phóng hoàn toàn kinh thành Thăng Long, bảo vệ vững chắc độc lập chủ quyền Đại Việt và đập tan hoàn toàn dã tâm bành trướng của nhà Mãn Thanh. "
            "Chính sách cải cách văn hóa giáo dục: Sau khi lên ngôi, vua Quang Trung ban hành Chiếu khuyến học nhằm chấn hưng nền giáo dục dân tộc, thành lập Viện Sùng chính do danh sĩ La Sơn Phu Tử Nguyễn Thiếp đứng đầu để dịch các tác phẩm chữ Hán sang chữ Nôm, đồng thời chính thức đề cao chữ Nôm thành văn tự quốc gia trong chiếu thư hành chính và thi cử."
        ),
    },
    {
        "id": "kb:deep_voice_ai_architecture",
        "passage": (
            "Hệ thống hỏi đáp tiếng nói tiếng Việt ViMMRC Voice Q&A được thiết kế theo kiến trúc chuỗi xử lý đầu-cuối (end-to-end pipeline) tích hợp chặt chẽ 4 phân hệ thông minh: "
            "1. Phân hệ Nhận dạng giọng nói (STT - Speech to Text): Ứng dụng mô hình nền tảng OpenAI Whisper-small được tinh chỉnh (fine-tune) bằng phương pháp thích ứng tham số cục bộ LoRA (Low-Rank Adaptation) trên hơn 50 giờ dữ liệu âm thanh giọng đọc tiếng Việt (VIVOS, VLSP và ViMMRC Audio). Trọng số sau khi merge được chuyển đổi sang định dạng CTranslate2 với kỹ thuật lượng tử hóa INT8 (INT8 quantization), giúp giảm 4 lần dung lượng bộ nhớ, tăng tốc độ xử lý nhanh hơn 4 lần trên CPU và đạt tỷ lệ lỗi từ WER 8.1% cùng bộ lọc phát hiện hoạt động giọng nói VAD. "
            "2. Phân hệ Truy xuất tri thức (Retrieval RAG 2 tầng): Tầng tri thức thứ nhất gồm 5.879 đoạn văn chọn lọc (ViMMRC, ViQuAD và thẻ tri thức chuyên sâu) với BM25s tối ưu siêu tham số k1=2.1, b=1.0, bigram_boost=0.4. Tầng tri thức thứ hai gồm 1.48 triệu đoạn văn Wikipedia tiếng Việt lưu dạng sharded BM25s kết hợp vector embedding ngữ nghĩa đa ngữ multilingual-e5-small 384 chiều (1.1 GB float16). Bộ tái xếp hạng sử dụng Cross-Encoder BAAI/bge-reranker-v2-m3 kết hợp cơ chế gating tin cậy raw > -2.0 và thuật toán n-gram phrase reranking khớp cụm từ liên tục. "
            "3. Phân hệ Đọc hiểu văn bản (MRC - Machine Reading Comprehension): Mô hình sinh tự do ViT5-base (Vietnamese T5, 220 triệu tham số) được fine-tune trên tập dữ liệu tổng hợp 27.164 câu hỏi ViMMRC và ViQuAD 2.0. ViT5 đạt độ chính xác Exact Match 41.05% và token F1 66.55% trên tập kiểm thử, áp dụng chiến lược trích chọn ngữ cảnh question_chunks cho văn bản dài và bộ lọc polish_answer giúp câu trả lời chuẩn ngữ pháp và dấu câu. "
            "4. Phân hệ Tổng hợp tiếng nói (TTS - Text to Speech): Tích hợp công nghệ hiện đại Matcha-TTS với kiến trúc Optimal Transport Conditional Flow Matching (OT-CFM) kết hợp bộ giải mã âm học HiFi-GAN sinh dạng sóng âm thanh tần số 22.050 Hz tự nhiên và truyền cảm; hỗ trợ Microsoft Edge Neural TTS giọng Hoài My, Nam Minh và cơ chế fallback tự động gTTS. "
            "Hiệu năng xử lý trên CPU: Khi chạy trong môi trường Docker container 4 luồng CPU, STT xử lý trong ~3 giây, truy xuất RAG ~6 giây (nếu tắt reranker còn ~0.5 giây), ViT5 đọc hiểu ~1.4 giây và TTS tổng hợp ~1.3 giây; toàn bộ mã nguồn và trọng số mô hình được đóng gói hoàn chỉnh bằng Docker và Docker Compose."
        ),
    },
    {
        "id": "kb:deep_geography_wonders",
        "passage": (
            "Đỉnh Fansipan (Phan Xi Păng) là đỉnh núi cao nhất Việt Nam và toàn bộ ba nước Đông Dương (Việt Nam, Lào, Campuchia) với độ cao đo đạc chính xác 3.143 mét so với mực nước biển, được mệnh danh là Nóc nhà Đông Dương (Roof of Indochina). "
            "Fansipan thuộc dãy núi Hoàng Liên Sơn, nằm giáp ranh giữa tỉnh Lào Cai và tỉnh Lai Châu, cách trung tâm thị xã Sa Pa khoảng 9 km về phía tây nam. "
            "Dãy Hoàng Liên Sơn là phần kéo dài về phía đông nam của dãy núi Himalaya, được hình thành trong đợt uốn nếp kiến tạo địa chất vào kỷ Permi - Trias cách đây hàng trăm triệu năm. "
            "Khí hậu trên đỉnh Fansipan mang tính chất á nhiệt đới và ôn đới núi cao, mùa đông nhiệt độ thường giảm sâu xuống dưới 0 độ C xuất hiện băng giá và tuyết rơi trắng xóa. "
            "Hang Sơn Đoòng là hang động tự nhiên lớn nhất thế giới tính theo thể tích mặt cắt không gian liên tục, tọa lạc tại Vườn quốc gia Phong Nha - Kẻ Bàng thuộc huyện Bố Trạch, tỉnh Quảng Bình, Việt Nam. "
            "Hang được một người dân địa phương tên là Hồ Khanh tình cờ phát hiện lần đầu tiên vào năm 1991 khi đi rừng tìm trầm, nhưng đến năm 2009 đoàn thám hiểm thuộc Hiệp hội Hang động Hoàng gia Anh (BCRA) do chuyên gia Howard Limbert dẫn đầu mới tiến hành khảo sát toàn diện và công bố với thế giới. "
            "Kích thước và hệ sinh thái độc nhất vô nhị của hang Sơn Đoòng: Hang có tổng chiều dài khảo sát gần 9 km, vòm hang nơi cao nhất đạt 200 mét và chiều rộng lên đến 150 mét, thể tích ước tính đạt 38.5 triệu mét khối (đủ chỗ chứa cả một tòa nhà chọc trời 40 tầng hoặc cả một khu phố trung tâm New York). "
            "Bên trong hang Sơn Đoòng có dòng sông ngầm ngọc bích chảy xiết, các khối măng đá và cột thạch nhũ khổng lồ cao tới hơn 70 mét. "
            "Đặc biệt, hang sở hữu hai hố sụt (doline) khổng lồ do trần hang sụp đổ cách đây hàng triệu năm, đón ánh nắng Mặt Trời chiếu rọi xuống tạo nên một khu rừng nhiệt đới nguyên sinh độc nhất vô nhị gọi là Vườn Địa Đàng (Garden of Edam), sở hữu vi khí hậu và hệ sinh vật đặc hữu riêng biệt không nơi nào trên Trái Đất có được."
        ),
    },
    {
        "id": "kb:deep_science_biology",
        "passage": (
            "Quá trình quang hợp (Photosynthesis) là cơ chế sinh học nền tảng của thực vật, tảo và một số vi khuẩn tự dưỡng sử dụng năng lượng ánh sáng Mặt Trời được hấp thụ bởi sắc tố diệp lục (chlorophyll) trong các bào quan lục lạp (chloroplast) của tế bào thực vật để tổng hợp chất hữu cơ. "
            "Cơ chế và phương trình hóa học của quang hợp: Cây xanh hấp thụ khí carbon dioxide (CO2) từ khí quyển thông qua các lỗ khí khổng phân bố ở bề mặt lá, đồng thời hút nước (H2O) và muối khoáng từ đất qua hệ thống rễ cây dẫn lên mạch gỗ. "
            "Dưới tác động của năng lượng photon ánh sáng qua chuỗi truyền electron, nước bị quang phân ly giải phóng khí oxy (O2) vào bầu khí quyển, đồng thời năng lượng được cố định tạo thành phân tử đường glucose (C6H12O6) theo phương trình tổng quát: 6CO2 + 6H2O -> C6H12O6 + 6O2. "
            "Hiện tượng hô hấp ban đêm ở thực vật: Vào ban đêm khi không có ánh sáng Mặt Trời, phản ứng pha sáng của quang hợp ngừng lại hoàn toàn. Lúc này, cây xanh duy trì hoạt động trao đổi chất thông qua quá trình hô hấp tế bào (cellular respiration) diễn ra trong bào quan ty thể (mitochondria), hấp thụ khí oxy (O2) và thải ra khí carbon dioxide (CO2). "
            "Do đó, trong không gian phòng ngủ đóng kín cửa không nên đặt quá nhiều chậu cây xanh để tránh hiện tượng cây tranh chấp dưỡng khí oxy với con người vào ban đêm. "
            "Tầm quan trọng sinh thái: Quang hợp là nguồn cung cấp dưỡng khí oxy chủ yếu duy trì sự sống trên Trái Đất, điều hòa khí hậu toàn cầu thông qua chu trình hấp thụ khí nhà kính carbon dioxide và cung cấp toàn bộ nguồn năng lượng sơ cấp cho chuỗi thức ăn trong sinh quyển."
        ),
    },
    {
        "id": "kb:deep_literature_culture",
        "passage": (
            "Kiệt tác Truyện Kiều (tên chữ Hán nguyên tác là Đoạn trường tân thanh, nghĩa là Tiếng kêu mới về nỗi đứt ruột) là tác phẩm đỉnh cao của nền văn học cổ điển Việt Nam do Đại thi hào Nguyễn Du (1765 - 1820) sáng tác. "
            "Tác phẩm được viết bằng chữ Nôm theo thể thơ lục bát truyền thống của dân tộc Việt Nam gồm tổng cộng 3.254 câu thơ. "
            "Cốt truyện và sáng tạo nghệ thuật vượt bậc: Nguyễn Du mượn cốt truyện từ tác phẩm văn xuôi Kim Vân Kiều truyện của Thanh Tâm Tài Nhân (thời nhà Thanh, Trung Quốc), nhưng đã tái sinh thành một kiệt tác thơ ca đậm đà bản sắc tâm hồn dân tộc Việt Nam. "
            "Truyện Kiều thể hiện tiếng kêu đớn đau cho số phận bất hạnh của người phụ nữ tài hoa bạc mệnh trong xã hội phong kiến đầy bất công và đồng tiền làm hoen ố nhân phẩm con người, đồng thời cất lên tiếng nói nhân đạo sâu sắc đòi quyền tự do yêu đương và hạnh phúc lứa đôi. "
            "Nghệ thuật đối sánh số phận qua đoạn trích Chị em Thúy Kiều: Nguyễn Du sử dụng bút pháp ước lệ tượng trưng tinh tế để dự báo số phận hai nhân vật. "
            "Thúy Vân được miêu tả với vẻ đẹp đoan trang, phúc hậu 'Khuôn trăng đầy đặn nét ngài nở nang / Hoa cười ngọc thốt đoan trang / Mây thua nước tóc tuyết nhường màu da' báo hiệu một cuộc đời êm đềm bình lặng; trong khi Thúy Kiều mang vẻ đẹp sắc sảo mặn mà 'Làn thu thủy nét xuân sơn / Hoa ghen thua thắm liễu hờn kém xanh' mang vẻ đẹp vượt trên chuẩn mực tự nhiên khiến tạo hóa đố kỵ, báo trước một số phận truân chuyên mười lăm năm lưu lạc đoạn trường. "
            "Dòng văn học hiện thực phê phán Việt Nam giai đoạn 1930 - 1945: Khắc họa chân thực số phận cùng cực của người nông dân dưới ách áp bức của thực dân phong kiến qua các tác phẩm bất hủ như Lão Hạc và Chí Phèo của nhà văn Nam Cao, Tắt đèn của nhà văn Ngô Tất Tố, thể hiện tấm lòng nhân đạo cao cả và niềm tin bất diệt vào bản chất lương thiện của con người."
        ),
    },
]


def main():
    print(f"Loading {KB_PATH}...")
    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {p["id"] for p in data["passages"]}
    added = 0
    updated = 0

    for card in DEEP_CARDS:
        card_id = card["id"]
        if card_id in existing_ids:
            for p in data["passages"]:
                if p["id"] == card_id:
                    p["passage"] = card["passage"]
                    updated += 1
                    break
        else:
            data["passages"].append(card)
            existing_ids.add(card_id)
            added += 1

    print(f"Added {added} deep cards, updated {updated} cards. Total passages: {len(data['passages'])}")
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


    print("Knowledge index enhancement complete!")


if __name__ == "__main__":
    main()
