"""Unit and integration tests for the STT server (speech-to-text_Luong/stt_server.py)."""
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
STT_DIR = ROOT / "speech-to-text_Luong"
if str(STT_DIR) not in sys.path:
    sys.path.insert(0, str(STT_DIR))

import stt_server


class STTServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(stt_server.app)

    def test_root_endpoint(self):
        # Directly test root function
        data = stt_server.root()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("service", data)
        self.assertIn("transcribe", data)

        # Also verify HTTP GET / returns 200 (JSON if standalone, HTML if static frontend mounted)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        if "application/json" in response.headers.get("content-type", ""):
            self.assertEqual(response.json().get("status"), "ok")
        else:
            self.assertIn("html", response.headers.get("content-type", "").lower())

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("model", data)
        self.assertIn("device", data)
        self.assertIn("model_loaded", data)

    def test_unsupported_content_type_returns_415(self):
        file_payload = ("test.txt", io.BytesIO(b"not audio data"), "text/plain")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 415)
        self.assertIn("Unsupported audio format", response.json().get("detail", ""))

    def test_empty_audio_returns_400(self):
        file_payload = ("empty.wav", io.BytesIO(b""), "audio/wav")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Empty audio", response.json().get("detail", ""))

    def test_oversized_audio_returns_413(self):
        large_chunk = b"0" * (stt_server.MAX_UPLOAD_BYTES + 10)
        file_payload = ("large.wav", io.BytesIO(large_chunk), "audio/wav")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 413)
        self.assertIn("Audio too large", response.json().get("detail", ""))

    @patch("stt_server.transcribe")
    def test_successful_transcription(self, mock_transcribe):
        mock_transcribe.return_value = "xin chào việt nam"
        dummy_wav = b"RIFF" + b"\x00" * 100
        file_payload = ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"text": "xin chào việt nam"})
        mock_transcribe.assert_called_once()

    @patch("stt_server.transcribe")
    def test_no_speech_detected_returns_422(self, mock_transcribe):
        mock_transcribe.return_value = ""
        dummy_wav = b"RIFF" + b"\x00" * 100
        file_payload = ("silence.wav", io.BytesIO(dummy_wav), "audio/wav")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 422)
        self.assertIn("No speech detected", response.json().get("detail", ""))

    @patch("stt_server.transcribe")
    def test_internal_error_returns_500(self, mock_transcribe):
        mock_transcribe.side_effect = RuntimeError("CTranslate2 unexpected failure")
        dummy_wav = b"RIFF" + b"\x00" * 100
        file_payload = ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")
        response = self.client.post("/api/stt", files={"file": file_payload})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Transcription failed", response.json().get("detail", ""))

    def test_model_lock_thread_safety(self):
        self.assertIsNotNone(stt_server.MODEL_LOCK)
        with stt_server.MODEL_LOCK:
            self.assertTrue(stt_server.MODEL_LOCK.locked())

    def test_allowed_content_types_contains_standard_formats(self):
        expected_formats = {"audio/wav", "audio/mpeg", "audio/ogg", "audio/webm", "audio/flac"}
        self.assertTrue(expected_formats.issubset(stt_server.ALLOWED_CONTENT_TYPES))


if __name__ == "__main__":
    unittest.main()
