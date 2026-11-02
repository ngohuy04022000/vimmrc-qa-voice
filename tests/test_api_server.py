"""Integration tests for the unified FastAPI api_server backend."""
import io
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from api_server import app


class ApiServerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("retrieval", data)
        self.assertIn("reader", data)
        self.assertIn("tts_engine", data)

    def test_retrieve_endpoint(self):
        response = self.client.post("/api/retrieve", json={"question": "Thủ đô Việt Nam", "top_k": 2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("passages", data)
        self.assertGreater(len(data["passages"]), 0)
        self.assertIn("id", data["passages"][0])
        self.assertIn("text", data["passages"][0])

    def test_answer_endpoint_open_ended(self):
        payload = {
            "question": "Thủ đô của Việt Nam là gì?",
            "passage": "Hà Nội là thủ đô của Việt Nam. Đây là trung tâm văn hóa và chính trị.",
        }
        response = self.client.post("/api/answer", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        self.assertTrue(len(data["answer"]) > 0)

    def test_tts_endpoint(self):
        payload = {
            "text": "Xin chào, đây là câu trả lời kiểm thử.",
            "engine": "edge",
        }
        response = self.client.post("/api/tts", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.headers.get("content-type"), ["audio/mpeg", "audio/wav"])
        self.assertGreater(len(response.content), 100)

    def test_chat_endpoint_multiturn(self):
        # Turn 1: greeting
        r1 = self.client.post("/api/chat", json={"question": "Xin chào trợ lý ảo!", "session_id": "test_sess_01", "reset": True})
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertTrue(d1["is_conversational"])
        self.assertIn("Xin chào", d1["answer"])

        # Turn 2: factual query
        r2 = self.client.post("/api/chat", json={"question": "Thủ đô của Việt Nam là gì?", "session_id": "test_sess_01"})
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertIn("answer", d2)
        self.assertTrue(len(d2["answer"]) > 0)

    def test_validation_errors(self):
        # Empty question in retrieve
        r = self.client.post("/api/retrieve", json={"question": "   "})
        self.assertEqual(r.status_code, 422)

        # Empty text in TTS
        r = self.client.post("/api/tts", json={"text": "   "})
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
