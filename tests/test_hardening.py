"""Tests cho các sửa cứng hoá api_server / synthesize (không nạp model thật)."""
import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import api_server
import synthesize as synth_module

client = TestClient(api_server.app)


@pytest.mark.parametrize("payload", [
    {"engine": "khong-co"},
    {"rate": "10%"},
    {"rate": "+1000%"},
    {"voice": "a b"},
    {"voice": "x" * 51},
])
def test_tts_invalid_fields_422(payload):
    assert client.post("/api/tts", json={"text": "xin chào", **payload}).status_code == 422


def test_tts_engine_case_insensitive_accepted():
    req = api_server.TTSRequest(text="a", engine="GTTS", voice="vi-VN-HoaiMyNeural", rate="-10%")
    assert req.engine == "GTTS"
    assert api_server.TTSRequest(text="a").engine is None


def test_env_float(monkeypatch, caplog):
    monkeypatch.setenv("X_FLOAT", "abc")
    with caplog.at_level(logging.WARNING):
        assert api_server._env_float("X_FLOAT", 0.4) == 0.4
    assert "X_FLOAT" in caplog.text
    monkeypatch.setenv("X_FLOAT", "0.7")
    assert api_server._env_float("X_FLOAT", 0.4) == 0.7
    monkeypatch.delenv("X_FLOAT")
    assert api_server._env_float("X_FLOAT", 0.4) == 0.4


def test_reader_fallback_logs_and_health(monkeypatch, caplog):
    def boom(*a, **k):
        raise RuntimeError("hong checkpoint")

    monkeypatch.delenv("MRC_CHECKPOINT", raising=False)
    monkeypatch.setattr(api_server, "_retriever", SimpleNamespace(passages=[]))
    monkeypatch.setattr(api_server, "_reader", None)
    monkeypatch.setattr(api_server, "find_default_checkpoint", lambda: "ckpt-gia")
    monkeypatch.setattr(api_server, "MRCClient", boom)
    with caplog.at_level(logging.ERROR):
        data = client.get("/api/health").json()
    assert data["reader"] == "lexical_baseline"
    assert "ckpt-gia" in caplog.text and "hong checkpoint" in caplog.text


def test_tts_failure_removes_mp3_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(api_server.tempfile, "gettempdir", lambda: str(tmp_path))

    def fake(text, output_path, **kw):
        Path(output_path).write_bytes(b"x")
        Path(output_path).with_suffix(".mp3").write_bytes(b"x")
        raise RuntimeError("loi")

    monkeypatch.setattr(api_server, "tts_synthesize", fake)
    r = client.post("/api/tts", json={"text": "xin chào", "engine": "matcha"})
    assert r.status_code == 502
    assert list(tmp_path.iterdir()) == []


def test_engine_cache_lock_and_single_creation(monkeypatch):
    assert hasattr(synth_module._ENGINE_LOCK, "acquire")
    calls = []
    monkeypatch.setattr(synth_module, "_ENGINE_CACHE", {})
    monkeypatch.setattr(synth_module, "get_tts_engine", lambda n, checkpoint_path=None: calls.append(n) or object())
    a = synth_module._get_engine("Fake")
    assert synth_module._get_engine("fake") is a
    assert calls == ["Fake"]


# ---- bảo mật tuỳ chọn (API_KEY / RATE_LIMIT_PER_MIN / CORS_ORIGINS), test trên FastAPI trần ----
def _secured_client(monkeypatch, **env):
    from fastapi import FastAPI

    for k in ("API_KEY", "RATE_LIMIT_PER_MIN", "CORS_ORIGINS"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    app = FastAPI()

    @app.get("/api/health")
    def _health():
        return {"status": "ok"}

    @app.post("/api/ask")
    def _ask():
        return {"answer": "x"}

    api_server._apply_security(app)
    return TestClient(app)


def test_security_default_off(monkeypatch):
    c = _secured_client(monkeypatch)
    for _ in range(5):
        assert c.post("/api/ask").status_code == 200
    assert c.get("/api/health").status_code == 200
    assert "access-control-allow-origin" not in c.get("/api/health", headers={"Origin": "https://a.com"}).headers


def test_security_api_key(monkeypatch):
    c = _secured_client(monkeypatch, API_KEY="s3cret")
    r = c.post("/api/ask")
    assert r.status_code == 401 and r.json() == {"detail": "invalid api key"}
    assert c.post("/api/ask", headers={"X-API-Key": "sai"}).status_code == 401
    assert c.post("/api/ask", headers={"X-API-Key": "s3cret"}).status_code == 200
    assert c.get("/api/health").status_code == 200


def test_security_rate_limit(monkeypatch):
    c = _secured_client(monkeypatch, RATE_LIMIT_PER_MIN="2")
    assert c.post("/api/ask").status_code == 200
    assert c.post("/api/ask").status_code == 200
    r = c.post("/api/ask")
    assert r.status_code == 429 and r.json() == {"detail": "rate limit exceeded"}
    assert int(r.headers["retry-after"]) >= 1
    assert c.get("/api/health").status_code == 200


def test_security_cors(monkeypatch):
    c = _secured_client(monkeypatch, CORS_ORIGINS="https://a.com, https://b.com")
    ok = c.get("/api/health", headers={"Origin": "https://b.com"})
    assert ok.headers["access-control-allow-origin"] == "https://b.com"
    assert "access-control-allow-origin" not in c.get("/api/health", headers={"Origin": "https://evil.com"}).headers


@pytest.mark.parametrize("bad", ["abc", "0", "-3"])
def test_security_rate_limit_invalid_is_off(monkeypatch, caplog, bad):
    c = _secured_client(monkeypatch, RATE_LIMIT_PER_MIN=bad)
    with caplog.at_level(logging.WARNING):
        for _ in range(4):
            assert c.post("/api/ask").status_code == 200
