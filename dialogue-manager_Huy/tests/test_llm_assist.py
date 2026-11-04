"""LLMAssist (Ollama) và cổng/kiểm chứng trong DialogueManager, dùng LLM giả."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import llm_assist  # noqa: E402
from dialogue import DialogueManager  # noqa: E402
from llm_assist import LLMAssist  # noqa: E402


class FakeAssist:
    """Thay LLMAssist: chỉ đoạn chứa 'Nguyễn Du' mới 'trả lời được'; verify trả theo cấu hình."""

    def __init__(self, verify=True):
        self._verify = verify
        self.verify_calls = 0

    def available(self):
        return True

    def supports(self, question, passage):
        return "Nguyễn Du" in passage

    def verify(self, question, passage, answer):
        self.verify_calls += 1
        return self._verify

    def answer(self, question, passage):
        return "Nguyễn Du."


class StubRetriever:
    def __init__(self, passages):
        self.passages = passages

    def search(self, question, top_k=3):
        return [{"id": f"p{i}", "passage": p, "score": 10.0 - i} for i, p in enumerate(self.passages[:top_k])]


class StubReader:
    def answer_question(self, question, passage):
        return "Hồ Chí Minh."


PASSAGES = ["Truyện Kiều là truyện thơ nổi tiếng của đại thi hào dân tộc Việt Nam, kể về cuộc đời Thúy Kiều.",
            "Truyện Kiều do Nguyễn Du sáng tác vào đầu thế kỷ XIX, gồm 3254 câu thơ lục bát."]
Q = "Truyện Kiều do ai sáng tác?"


def test_gate_skips_passage_that_does_not_answer():
    dm = DialogueManager(StubRetriever(PASSAGES), StubReader(), assist=FakeAssist(), assist_verify=False)
    result = dm.respond(Q)
    assert result["kind"] == "qa" and "Nguyễn Du" in result["passage"]["text"]


def test_gate_refuses_when_no_passage_answers():
    dm = DialogueManager(StubRetriever(PASSAGES[:1]), StubReader(), assist=FakeAssist(), assist_verify=False)
    assert dm.respond(Q)["kind"] == "unknown"


def test_verify_replaces_rejected_answer():
    dm = DialogueManager(StubRetriever(PASSAGES), StubReader(), assist=FakeAssist(verify=False), assist_gate=False)
    result = dm.respond(Q)
    assert "Nguyễn Du" in result["answer"] and result["llm"]["replaced"] == "Hồ Chí Minh."


def test_no_assist_leaves_behaviour_unchanged():
    dm = DialogueManager(StubRetriever(PASSAGES), StubReader())
    assert dm.respond(Q)["llm"] == {}


def test_unreachable_ollama_returns_none(monkeypatch):
    def boom(*a, **k):
        raise llm_assist.requests.ConnectionError("down")

    monkeypatch.setattr(llm_assist.requests, "get", boom)
    monkeypatch.setattr(llm_assist.requests, "post", boom)
    assist = LLMAssist()
    assert not assist.available()
    assert assist.supports("q", "p") is None and assist.fix_transcript("chuyện kiều") == "chuyện kiều"


def test_disabled_assist_never_calls_network(monkeypatch):
    monkeypatch.setattr(llm_assist.requests, "get", lambda *a, **k: 1 / 0)
    assert LLMAssist(enabled=False).available() is False


def test_fix_transcript_rejects_rewritten_sentence(monkeypatch):
    assist = LLMAssist()
    monkeypatch.setattr(assist, "_gen", lambda *a, **k: "Một câu hoàn toàn khác về thời tiết hôm nay ở Hà Nội")
    assert assist.fix_transcript("chuyện kiều do ai viết") == "chuyện kiều do ai viết"
    monkeypatch.setattr(assist, "_gen", lambda *a, **k: "Truyện Kiều do ai viết")
    assert assist.fix_transcript("chuyện kiều do ai viết") == "Truyện Kiều do ai viết"


def test_supports_parses_yes_no(monkeypatch):
    assist = LLMAssist()
    for reply, expect in (("CÓ", True), ("Có.", True), ("KHÔNG", False), ("Không", False), ("???", None)):
        monkeypatch.setattr(assist, "_gen", lambda *a, _r=reply, **k: _r)
        assert assist.supports("q", "p") is expect, reply


def test_realtime_question_is_refused_with_assist():
    dm = DialogueManager(StubRetriever(PASSAGES), StubReader(), assist=FakeAssist(), assist_verify=False)
    # đoạn có "Nguyễn Du" nên cổng LLM sẽ cho qua: chỉ luật thời gian thực mới từ chối được
    assert dm.respond("Truyện Kiều do ai sáng tác hôm nay?")["kind"] == "unknown"
    assert dm.respond(Q)["kind"] == "qa"
    assert DialogueManager(StubRetriever(PASSAGES), StubReader()).respond("Truyện Kiều do ai sáng tác hiện nay?")["kind"] == "qa"
