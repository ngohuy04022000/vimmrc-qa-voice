"""Unit tests for DialogueContextManager and multi-turn dialogue handling."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("scripts", "retrieval-model_Huy", "mrc-model_Huy"):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from dialogue_manager import DialogueContextManager, DialogueSession
from retrieval_client import Retriever
from mrc_client import LexicalBaselineClient


class DialogueContextManagerTests(unittest.TestCase):
    def setUp(self):
        self.mgr = DialogueContextManager()

    def test_session_creation_and_reset(self):
        s = self.mgr.get_session("test_sess_01")
        self.assertEqual(s.session_id, "test_sess_01")
        self.assertEqual(len(s.turns), 0)

        s.add_turn("user", "Xin chào")
        s.add_turn("assistant", "Chào bạn")
        self.assertEqual(len(s.turns), 2)

        self.mgr.reset_session("test_sess_01")
        self.assertEqual(len(s.turns), 0)
        self.assertIsNone(s.active_topic)

    def test_entity_extraction(self):
        self.assertEqual(
            self.mgr.extract_salient_entity("Hãy cho tôi biết về vua Quang Trung"),
            "Vua Quang Trung",
        )
        self.assertEqual(
            self.mgr.extract_salient_entity("Hang Sơn Đoòng nằm ở đâu?"),
            "Hang Sơn Đoòng",
        )
        self.assertEqual(
            self.mgr.extract_salient_entity("Kiến trúc của mô hình Whisper thế nào?"),
            "Mô hình Whisper",
        )
        self.assertIsNone(self.mgr.extract_salient_entity("Hôm nay trời đẹp quá"))

    def test_anaphora_detection(self):
        self.assertTrue(self.mgr.has_anaphora("Chiến thuật của ông ấy ra sao?"))
        self.assertTrue(self.mgr.has_anaphora("Hang động này được phát hiện vào năm nào?"))
        self.assertTrue(self.mgr.has_anaphora("Mô hình này đạt độ chính xác bao nhiêu?"))
        self.assertTrue(self.mgr.has_anaphora("Tại sao lại diễn ra như vậy?"))
        self.assertFalse(self.mgr.has_anaphora("Thủ đô của Việt Nam là thành phố nào?"))

    def test_query_reformulation_with_context(self):
        session = self.mgr.get_session("history_session")

        # Turn 1: mentions Quang Trung explicitly
        q1 = "Vua Quang Trung đại phá quân Thanh vào năm nào?"
        ref1, was_ref1 = self.mgr.reformulate_query(q1, session)
        self.assertEqual(session.active_topic, "Vua Quang Trung")
        self.assertFalse(was_ref1)

        # Turn 2: uses pronoun "ông ấy"
        q2 = "Chiến thuật hành quân thần tốc của ông ấy diễn ra như thế nào?"
        ref2, was_ref2 = self.mgr.reformulate_query(q2, session)
        self.assertTrue(was_ref2)
        self.assertIn("Quang Trung", ref2)
        self.assertIn("Chiến thuật hành quân thần tốc của ông ấy", ref2)

    def test_multi_turn_chat_flow_with_retriever(self):
        passages = [
            {
                "id": "doc:quangtrung",
                "passage": "Vua Quang Trung tức Nguyễn Huệ đại phá 29 vạn quân Thanh vào năm 1789 tại trận Ngọc Hồi Đống Đa.",
            },
            {
                "id": "doc:quangtrung_tactics",
                "passage": "Vua Quang Trung tổ chức hành quân thần tốc bằng cách chia quân thành từng tốp ba người thay phiên nhau cáng nghỉ.",
            },
        ]
        retriever = Retriever(passages)
        reader = LexicalBaselineClient()

        sess_id = "flow_test_sess"
        self.mgr.reset_session(sess_id)

        # Turn 1: Greeting
        res1 = self.mgr.chat_turn("Xin chào bạn!", session_id=sess_id, retriever=retriever, reader=reader)
        self.assertTrue(res1["is_conversational"])
        self.assertIn("Xin chào", res1["answer"])

        # Turn 2: General question establishing topic
        res2 = self.mgr.chat_turn(
            "Vua Quang Trung đại phá quân Thanh vào năm nào?",
            session_id=sess_id,
            retriever=retriever,
            reader=reader,
        )
        self.assertFalse(res2["is_conversational"])
        self.assertEqual(res2["active_topic"], "Vua Quang Trung")
        self.assertEqual(res2["passage_id"], "doc:quangtrung")

        # Turn 3: Follow-up question with pronoun
        res3 = self.mgr.chat_turn(
            "Chiến thuật hành quân của ông ấy có điểm gì đặc biệt?",
            session_id=sess_id,
            retriever=retriever,
            reader=reader,
        )
        self.assertFalse(res3["is_conversational"])
        self.assertTrue(res3["was_reformulated"])
        self.assertEqual(res3["passage_id"], "doc:quangtrung_tactics")

        # Turn 4: Gratitude in context
        res4 = self.mgr.chat_turn("Cảm ơn bạn rất nhiều nhé!", session_id=sess_id, retriever=retriever, reader=reader)
        self.assertTrue(res4["is_conversational"])
        self.assertIn("Quang Trung", res4["answer"])


if __name__ == "__main__":
    unittest.main()
