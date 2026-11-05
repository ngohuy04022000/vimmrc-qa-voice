"""Kiểm thử tầng hội thoại: không cần mô hình, chạy trên kho kiến thức mẫu."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
for folder in (HERE, ROOT / "retrieval-model_Huy", ROOT / "text-to-speech_Duy" / "src"):
    sys.path.insert(0, str(folder))

from answer_composer import (HeuristicReader, compose_answer, fill_template, parse_quantity,  # noqa: E402
                             split_sentences, summarize)
from dialogue import DialogueManager, parse_comparison, split_multi_question, yesno_claims  # noqa: E402
from retrieval_client import Retriever  # noqa: E402
from smalltalk import detect_intent, try_arithmetic  # noqa: E402
from utterance import clean_utterance, question_type  # noqa: E402

SEED = json.loads((HERE / "eval" / "seed_kb.json").read_text(encoding="utf-8"))


class UtteranceTests(unittest.TestCase):
    def test_clean_strips_fillers_and_politeness(self):
        self.assertEqual(clean_utterance("Ừm cho mình hỏi là thủ đô của Pháp là gì vậy bạn?"), "thủ đô của Pháp là gì")
        self.assertEqual(clean_utterance("Bạn có biết Hà Nội ở đâu không?"), "Hà Nội ở đâu")
        self.assertEqual(clean_utterance("tại sao lại như thế"), "tại sao lại như thế")  # 'như thế' giữ nguyên

    def test_question_types(self):
        cases = {"Vì sao bầu trời có màu xanh?": "why", "Fansipan cao bao nhiêu?": "quantity",
                 "Hồ Chí Minh sinh năm nào?": "time", "Ai phát minh ra bóng đèn?": "person",
                 "Vịnh Hạ Long ở đâu?": "location", "Có phải Hà Nội là thủ đô không?": "yesno",
                 "Nội dung chính của đoạn văn là gì?": "summary", "Giới thiệu về Huế": "describe",
                 "Máy bay được phát minh khi nào?": "time"}
        for q, expected in cases.items():
            self.assertEqual(question_type(q), expected, q)


class SmalltalkTests(unittest.TestCase):
    def test_intents_match_whole_utterance_only(self):
        self.assertEqual(detect_intent("Xin chào bạn!")[0], "greeting")
        self.assertEqual(detect_intent("chao ban")[0], "greeting")  # gõ không dấu
        self.assertEqual(detect_intent("Mình đi đây, bye bye")[0], "goodbye")
        self.assertIsNone(detect_intent("Bạn có biết Hà Nội ở đâu không?"))
        self.assertIsNone(detect_intent("Sông nào dài nhất thế giới?"))
        # câu xã giao dài vẫn nhận ra, nhưng câu hỏi chứa từ khóa thì không
        self.assertEqual(detect_intent("Hay quá, cảm ơn bạn nhé, kiến thức rất thú vị")[0], "thanks")
        self.assertEqual(detect_intent("Hẹn gặp lại bạn lần sau.")[0], "goodbye")
        self.assertEqual(detect_intent("Xin chào, tôi muốn tìm hiểu về Fansipan")[0], "greeting")
        self.assertIsNone(detect_intent("Ai đã nói cảm ơn trước tiên?"))

    def test_arithmetic(self):
        self.assertEqual(try_arithmetic("12 nhân 12 bằng bao nhiêu"), "12 nhân 12 bằng 144.")
        self.assertEqual(try_arithmetic("một trăm hai mươi chia ba"), "120 chia 3 bằng 40.")
        self.assertEqual(try_arithmetic("100 chia 0"), "Không thể chia cho số không.")
        self.assertIsNone(try_arithmetic("Hà Nội cộng đồng"))


class ComposerTests(unittest.TestCase):
    def test_fill_template_makes_full_sentence(self):
        self.assertEqual(fill_template("Thủ đô của Nhật Bản là gì?", "Tokyo"), "Thủ đô của Nhật Bản là Tokyo.")
        self.assertEqual(fill_template("Việt Nam có bao nhiêu dân tộc?", "54 dân tộc"), "Việt Nam có 54 dân tộc.")
        self.assertEqual(fill_template("Ai là người phát minh ra bóng đèn?", "Thomas Edison"),
                         "Thomas Edison là người phát minh ra bóng đèn.")
        self.assertEqual(fill_template("Fansipan nằm ở đâu?", "dãy Hoàng Liên Sơn"), "Fansipan nằm ở dãy Hoàng Liên Sơn.")

    def test_reader_picks_typed_span(self):
        p = "Nguyễn Du sinh năm 1765 và mất năm 1820, là đại thi hào. Truyện Kiều gồm 3.254 câu thơ."
        r = HeuristicReader()
        self.assertIn("1820", r.answer_question("Nguyễn Du mất năm nào?", p))
        self.assertIn("3.254", r.answer_question("Truyện Kiều có bao nhiêu câu thơ?", p))

    def test_why_answer_keeps_evidence(self):
        p = next(x["passage"] for x in SEED if x["id"] == "seed:sky")
        out = compose_answer("Vì sao bầu trời có màu xanh?", "tán xạ", p)
        self.assertIn("tán xạ", out)
        self.assertTrue(out.endswith("."))

    def test_sentence_split_keeps_decimals(self):
        self.assertEqual(len(split_sentences("Núi cao 3.143 m. Sông dài 4,35 km.")), 2)
        self.assertTrue(summarize("Câu một. Câu hai. Câu ba. Câu bốn.", limit=2))

    def test_parse_quantity(self):
        self.assertEqual(parse_quantity("3.143 m"), 3143)
        self.assertEqual(parse_quantity("khoảng 8,5 triệu người"), 8_500_000)


class DecompositionTests(unittest.TestCase):
    def test_comparison_parsing(self):
        c = parse_comparison("Sông Hồng hay sông Mê Kông dài hơn?")
        self.assertEqual((c["a"], c["b"], c["adj"]), ("Sông Hồng", "sông Mê Kông", "dài"))
        c = parse_comparison("Giữa Hà Nội và Thành phố Hồ Chí Minh, thành phố nào đông dân hơn?")
        self.assertEqual((c["a"], c["b"], c["adj"]), ("Hà Nội", "Thành phố Hồ Chí Minh", "đông dân"))
        self.assertIsNone(parse_comparison("Thủ đô của Pháp là gì?"))

    def test_multi_question_inherits_subject(self):
        parts = split_multi_question("Fansipan cao bao nhiêu và nằm ở tỉnh nào?")
        self.assertEqual(parts, ["Fansipan cao bao nhiêu", "Fansipan nằm ở tỉnh nào"])
        self.assertEqual(split_multi_question("Sông Nin dài bao nhiêu? Nó đổ ra biển nào?")[1], "Sông Nin đổ ra biển nào")
        self.assertEqual(len(split_multi_question("Hà Nội và Huế ở đâu?")), 1)  # 'và' nối chủ ngữ, không tách

    def test_yesno_claims(self):
        self.assertEqual(yesno_claims("Có phải Tokyo là thủ đô của Hàn Quốc không?"), ["Tokyo là thủ đô của Hàn Quốc"])


class DialogueTests(unittest.TestCase):
    def setUp(self):
        self.dm = DialogueManager(Retriever(SEED), seed=0)

    def ask(self, text, sid="t"):
        return self.dm.respond(text, sid)

    def test_follow_up_entity_substitution(self):
        self.assertIn("Tokyo", self.ask("Thủ đô của Nhật Bản là gì?")["answer"])
        r = self.ask("Còn Hàn Quốc thì sao?")
        self.assertEqual(r["resolved_question"], "Thủ đô của Hàn Quốc là gì")
        self.assertIn("Seoul", r["answer"])

    def test_pronoun_refers_to_person_in_answer(self):
        self.assertIn("Edison", self.ask("Ai phát minh ra bóng đèn sợi đốt?")["answer"])
        r = self.ask("Ông ấy sinh năm nào?")
        self.assertIn("Edison", r["resolved_question"])
        self.assertIn("1847", r["answer"])

    def test_sessions_are_isolated(self):
        self.ask("Thủ đô của Nhật Bản là gì?", "a")
        r = self.ask("Còn Hàn Quốc thì sao?", "b")  # phiên b chưa có ngữ cảnh
        self.assertNotIn("Seoul", r["answer"])

    def test_comparison_answer(self):
        r = self.ask("Cá voi xanh hay voi châu Phi nặng hơn?")
        self.assertEqual(r["kind"], "compare")
        self.assertTrue(r["answer"].startswith("Cá voi xanh nặng hơn"))

    def test_yes_no(self):
        self.assertTrue(self.ask("Lào có giáp biển không?")["answer"].startswith("Không"))
        self.assertTrue(self.ask("Sao Mộc là hành tinh lớn nhất phải không?")["answer"].startswith("Đúng"))

    def test_unknown_instead_of_guess(self):
        for q in ("Giá vàng hôm nay bao nhiêu?", "Bitcoin được tạo ra năm nào?"):
            self.assertEqual(self.ask(q)["kind"], "unknown", q)

    def test_user_passage_summary(self):
        p = "Làng gốm Bát Tràng ở Hà Nội. Làng có lịch sử hơn 700 năm. Gốm nổi tiếng vì men đẹp."
        r = self.dm.respond("Nội dung chính của đoạn văn là gì?", "p", p)
        self.assertEqual(r["kind"], "summary")
        self.assertIn("Bát Tràng", r["answer"])

    def test_expand_and_repeat(self):
        self.ask("Vì sao bầu trời có màu xanh?")
        expanded = self.ask("Giải thích rõ hơn đi")
        self.assertEqual(expanded["kind"], "expand")
        self.assertEqual(self.ask("Nhắc lại đi")["answer"], expanded["answer"])

    def test_answers_are_tts_clean(self):
        from normalizer import normalize_vietnamese_text
        import re
        for q in ("Sa mạc Sahara rộng bao nhiêu?", "Công thức hóa học của nước là gì?", "Fansipan cao bao nhiêu?"):
            spoken = normalize_vietnamese_text(self.ask(q)["answer"])
            self.assertFalse(re.search(r"\d|[²³°%]", spoken), spoken)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            self.ask("   ")


class EvalSetTests(unittest.TestCase):
    """Chốt chất lượng: bộ phát triển >= 95% mục đạt, bộ held-out >= 90% (offline)."""

    def run_set(self, name):
        sys.path.insert(0, str(HERE))
        from eval_dialogue import check_turn
        items = json.loads((HERE / "eval" / name).read_text(encoding="utf-8"))["items"]
        dm = DialogueManager(Retriever(SEED), seed=0)
        ok = 0
        for item in items:
            good = True
            for turn in item["turns"]:
                r = dm.respond(turn["user"], item["id"], item.get("passage"))
                good &= not check_turn(r["answer"], r["kind"], turn)
            ok += good
        return ok, len(items)

    def test_dev_set(self):
        ok, n = self.run_set("conversations.json")
        self.assertGreaterEqual(n, 150)
        self.assertGreaterEqual(ok / n, 0.95)

    def test_heldout_set(self):
        ok, n = self.run_set("conversations_heldout.json")
        self.assertGreaterEqual(ok / n, 0.90)


if __name__ == "__main__":
    unittest.main()
