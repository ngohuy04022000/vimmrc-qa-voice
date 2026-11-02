"""Unit tests for ConversationalIntentRouter and polish_answer."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from intent_router import ConversationalIntentRouter, polish_answer, rerank_hits, compute_phrase_overlap_score


class IntentRouterTests(unittest.TestCase):
    def test_greeting_intent(self):
        queries = ["Xin chào!", "Chào bạn nhé", "chào buổi sáng", "Hello", "Hi"]
        for q in queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(ans, f"Failed to match greeting for: {q}")
            self.assertIn("Xin chào", ans)

    def test_identity_intent(self):
        queries = ["Bạn là ai?", "Bạn tên là gì vậy", "Ai đã tạo ra bạn?"]
        for q in queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(ans, f"Failed to match identity for: {q}")
            self.assertIn("trợ lý", ans)

    def test_capabilities_intent(self):
        queries = ["Bạn có thể làm được gì?", "Bạn giúp được gì cho tôi?", "Hướng dẫn sử dụng"]
        for q in queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(ans, f"Failed to match capability for: {q}")
            self.assertIn("lắng nghe", ans)

    def test_gratitude_intent(self):
        queries = ["Cảm ơn bạn nhé", "Thank you", "Bạn giỏi quá!"]
        for q in queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(ans, f"Failed to match gratitude for: {q}")
            self.assertIn("Rất vui", ans)

    def test_farewell_intent(self):
        queries = ["Tạm biệt nhé", "Hẹn gặp lại", "Bye bye!"]
        for q in queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(ans, f"Failed to match farewell for: {q}")
            self.assertIn("Tạm biệt", ans)

    def test_factual_query_not_matched_as_conversation(self):
        factual_queries = [
            "Thủ đô của Việt Nam là gì?",
            "Ai là tác giả của tác phẩm Truyện Kiều?",
            "Chiến thắng Bạch Đằng diễn ra vào năm nào?",
            "Đỉnh núi cao nhất Việt Nam là đỉnh núi nào?",
            "Nước sôi ở nhiệt độ bao nhiêu độ C?",
        ]
        for q in factual_queries:
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNone(ans, f"Factual question incorrectly matched as intent: {q}")

    def test_polish_answer(self):
        # Empty or whitespace answer gives graceful fallback
        self.assertIn("Xin lỗi", polish_answer(""))
        self.assertIn("Xin lỗi", polish_answer("   "))

        # Raw lowercase fragment is capitalized and punctuated
        self.assertEqual(polish_answer("hà nội"), "Hà nội.")
        self.assertEqual(polish_answer("Nguyễn Du."), "Nguyễn Du.")

        # Strips enclosing quotes
        self.assertEqual(polish_answer('"Hà Nội"'), "Hà Nội.")
        self.assertEqual(polish_answer(" - Thăng Long"), "Thăng Long.")

    def test_rerank_hits(self):
        question = "Ai là tác giả của tác phẩm Truyện Kiều?"
        hits = [
            {
                "id": "doc1",
                "passage": "Một số tác phẩm văn học thời trung đại Việt Nam được nhiều người biết đến.",
                "score": 5.0,
            },
            {
                "id": "doc2",
                "passage": "Đại thi hào Nguyễn Du là tác giả của tác phẩm Truyện Kiều kinh điển.",
                "score": 4.5,
            },
        ]
        reranked = rerank_hits(question, hits, top_k=1)
        self.assertEqual(len(reranked), 1)
        self.assertEqual(reranked[0]["id"], "doc2")
        self.assertGreater(reranked[0]["phrase_bonus"], 0.0)



if __name__ == "__main__":
    unittest.main()
