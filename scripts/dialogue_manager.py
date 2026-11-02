"""Multi-Turn Dialogue and Context Manager for ViMMRC Voice Q&A.

Supports:
1. Multi-turn conversation sessions with persistent context & history tracking.
2. Contextual query reformulation resolving anaphora and pronouns (ông ấy, nơi đó, mô hình này, v.v.).
3. Conversational intent awareness with context-sensitive responses.
4. Seamless integration with QAPipeline, Retriever, and MRC ViT5.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from intent_router import (
    ConversationalIntentRouter,
    polish_answer,
    rerank_hits,
    remove_accents,
)

logger = logging.getLogger("dialogue_manager")


class DialogueSession:
    """Stores the turns and context state of a single conversation session."""

    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.turns: List[Dict[str, Any]] = []
        self.active_topic: Optional[str] = None
        self.active_entities: List[str] = []

    def add_turn(
        self,
        role: str,
        text: str,
        intent: Optional[str] = None,
        is_conversational: bool = False,
        passage_id: Optional[str] = None,
    ) -> None:
        self.turns.append({
            "turn_index": len(self.turns) + 1,
            "role": role,
            "text": text,
            "intent": intent,
            "is_conversational": is_conversational,
            "passage_id": passage_id,
        })

    def reset(self) -> None:
        self.turns.clear()
        self.active_topic = None
        self.active_entities.clear()


class DialogueContextManager:
    """Coordinates multi-turn dialogue flow, query reformulation, and pipeline execution."""

    # Common anaphoric pronouns and demonstratives in Vietnamese (unaccented regex)
    ANAPHORA_PATTERNS = [
        r"\bong ay\b",
        r"\bba ay\b",
        r"\bong\b",
        r"\bnguoi do\b",
        r"\bnhan vat nay\b",
        r"\bvi tuong nay\b",
        r"\bvi vua nay\b",
        r"\bnoi do\b",
        r"\bnoi nay\b",
        r"\bdia danh nay\b",
        r"\bhang dong nay\b",
        r"\bngon nui nay\b",
        r"\bhe thong nay\b",
        r"\bmo hinh nay\b",
        r"\bcong nghe nay\b",
        r"\bcong nghe do\b",
        r"\btran danh nay\b",
        r"\bchien dich nay\b",
        r"\bqua trinh nay\b",
        r"\bhien tuong nay\b",
        r"\bkiet tac nay\b",
        r"\btac pham nay\b",
        r"\bsau do\b",
        r"\btai sao\b",
        r"\bnhu the nao\b",
        r"\bra sao\b",
    ]

    # Predefined salient entity patterns for Vietnamese domains
    KNOWN_ENTITY_PATTERNS = [
        (r"\bquang trung\b|\bnguyen hue\b", "Vua Quang Trung"),
        (r"\bngo quyen\b", "Ngô Quyền"),
        (r"\bly thuong kiet\b", "Lý Thường Kiệt"),
        (r"\btran quoc tuan\b|\btran hung dao\b", "Trần Hưng Đạo"),
        (r"\bdinh bo linh\b|\bdinh tien hoang\b", "Đinh Bộ Lĩnh"),
        (r"\bly thai to\b", "Lý Thái Tổ"),
        (r"\bho chi minh\b|\bbac ho\b", "Chủ tịch Hồ Chí Minh"),
        (r"\bfansipan\b|\bphan xi pang\b", "Đỉnh Fansipan"),
        (r"\bson doong\b|\bhang son doong\b", "Hang Sơn Đoòng"),
        (r"\bha noi\b", "Thành phố Hà Nội"),
        (r"\bphu quoc\b", "Đảo Phú Quốc"),
        (r"\bvinh ha long\b", "Vịnh Hạ Long"),
        (r"\btruyen kieu\b|\bdoan truong tan thanh\b", "Truyện Kiều"),
        (r"\bnam cao\b|\blao hac\b|\bchi pheo\b", "Nhà văn Nam Cao"),
        (r"\bngo tat to\b|\btat den\b", "Tác phẩm Tắt đèn"),
        (r"\bquang hop\b", "Quá trình quang hợp"),
        (r"\bho hap\b", "Quá trình hô hấp thực vật"),
        (r"\bwhisper\b", "Mô hình Whisper"),
        (r"\bvit5\b", "Mô hình ViT5"),
        (r"\bmatcha\b|\bmatcha tts\b", "Matcha-TTS"),
        (r"\brag\b|\btruy xuat\b", "Kiến trúc RAG"),
        (r"\bvimmrc\b", "Hệ thống ViMMRC"),
    ]

    def __init__(self, pipeline: Any = None):
        self.pipeline = pipeline
        self.sessions: Dict[str, DialogueSession] = {}

    def get_session(self, session_id: str = "default") -> DialogueSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = DialogueSession(session_id)
        return self.sessions[session_id]

    def reset_session(self, session_id: str = "default") -> None:
        if session_id in self.sessions:
            self.sessions[session_id].reset()

    def extract_salient_entity(self, text: str) -> Optional[str]:
        """Detect key topic entities from the query text."""
        norm = remove_accents(text).lower()
        for pat, canonical in self.KNOWN_ENTITY_PATTERNS:
            if re.search(pat, norm):
                return canonical
        return None

    def has_anaphora(self, text: str) -> bool:
        """Check if query contains demonstrative or personal pronouns requiring context."""
        norm = remove_accents(text).lower()
        clean = " " + " ".join(re.sub(r"[^\w\s]", " ", norm).split()) + " "
        return any(re.search(pat, clean) for pat in self.ANAPHORA_PATTERNS)

    def reformulate_query(self, question: str, session: DialogueSession) -> Tuple[str, bool]:
        """Reformulate query by incorporating conversation context if anaphora is present.

        Returns (reformulated_query, was_reformulated).
        """
        # First, extract any explicit entity present in the current question
        current_entity = self.extract_salient_entity(question)
        if current_entity:
            session.active_topic = current_entity
            if current_entity not in session.active_entities:
                session.active_entities.append(current_entity)

        # Check if question needs contextual resolution
        needs_context = self.has_anaphora(question)
        if needs_context and session.active_topic:
            # Check if active topic is already explicitly named in the question
            norm_q = remove_accents(question).lower()
            norm_topic = remove_accents(session.active_topic).lower()
            topic_keywords = [w for w in re.findall(r"\w+", norm_topic) if len(w) > 2]
            already_contains_topic = any(kw in norm_q for kw in topic_keywords)

            if not already_contains_topic:
                reformulated = f"{session.active_topic} {question}"
                return (reformulated, True)

        return (question, False)

    def chat_turn(
        self,
        question: str,
        session_id: str = "default",
        retriever: Any = None,
        reader: Any = None,
    ) -> Dict[str, Any]:
        """Process one conversational turn in the multi-turn session."""
        session = self.get_session(session_id)
        q_clean = question.strip()

        # 1. Check greeting with topic initiation
        norm_q = remove_accents(q_clean).lower()
        starts_with_greeting = bool(re.match(r"^\s*(xin chao|chao (ban|em|tro ly|quy khach)|hello|hi)\b", norm_q))
        salient_entity = self.extract_salient_entity(q_clean)

        if starts_with_greeting and salient_entity and len(q_clean.split()) <= 18:
            session.active_topic = salient_entity
            if salient_entity not in session.active_entities:
                session.active_entities.append(salient_entity)
            response_text = (
                f"Xin chào bạn! Tôi rất sẵn lòng hỗ trợ bạn tìm hiểu chuyên sâu về {salient_entity}. "
                "Bạn muốn tìm hiểu về khía cạnh nào trước?"
            )
            session.add_turn("user", q_clean, intent="greeting", is_conversational=True)
            session.add_turn("assistant", response_text, intent="greeting", is_conversational=True)
            return {
                "session_id": session_id,
                "turn_index": len(session.turns) // 2,
                "question": q_clean,
                "answer": response_text,
                "reformulated_query": q_clean,
                "was_reformulated": False,
                "is_conversational": True,
                "intent": "greeting",
                "passage_id": "intent:conversational",
                "active_topic": session.active_topic,
            }

        # 2. Check general conversational intent
        intent_match = ConversationalIntentRouter.match_intent(q_clean)
        if intent_match:
            intent_name, base_response = intent_match
            # Add multi-turn context flavor for gratitude if topic exists
            if intent_name == "gratitude" and session.active_topic:
                response_text = (
                    f"Rất vui được hỗ trợ bạn tìm hiểu chi tiết về {session.active_topic}! "
                    "Nếu bạn còn bất kỳ câu hỏi nào khác, hãy cứ hỏi tôi nhé."
                )
            else:
                response_text = base_response

            session.add_turn("user", q_clean, intent=intent_name, is_conversational=True)
            session.add_turn("assistant", response_text, intent=intent_name, is_conversational=True)

            return {
                "session_id": session_id,
                "turn_index": len(session.turns) // 2,
                "question": q_clean,
                "answer": response_text,
                "reformulated_query": q_clean,
                "was_reformulated": False,
                "is_conversational": True,
                "intent": intent_name,
                "passage_id": "intent:conversational",
                "active_topic": session.active_topic,
            }

        # 2. Contextual query reformulation for factual queries
        reformulated_q, was_reformulated = self.reformulate_query(q_clean, session)

        # 3. Retrieve relevant knowledge passage
        active_retriever = retriever or (self.pipeline.retriever if self.pipeline else None)
        active_reader = reader or (self.pipeline.reader if self.pipeline else None)

        if not active_retriever:
            raise RuntimeError("Retriever instance required for factual Q&A turn")

        raw_hits = active_retriever.search(reformulated_q, top_k=5)
        reranked = rerank_hits(reformulated_q, raw_hits, top_k=1)

        if reranked and reranked[0]["score"] > 0:
            top_hit = reranked[0]
            if active_reader:
                raw_ans = active_reader.answer_question(q_clean, top_hit["passage"])
                answer = polish_answer(raw_ans, q_clean)
            else:
                answer = polish_answer(top_hit["passage"][:200], q_clean)
            passage_id = top_hit["id"]
            retrieval_score = top_hit["score"]
        else:
            answer = "Xin lỗi, tôi chưa tìm thấy thông tin phù hợp cho câu hỏi này trong kho tri thức."
            passage_id = None
            retrieval_score = 0.0

        # Update session
        session.add_turn("user", q_clean, is_conversational=False)
        session.add_turn("assistant", answer, is_conversational=False, passage_id=passage_id)

        return {
            "session_id": session_id,
            "turn_index": len(session.turns) // 2,
            "question": q_clean,
            "answer": answer,
            "reformulated_query": reformulated_q,
            "was_reformulated": was_reformulated,
            "is_conversational": False,
            "intent": None,
            "passage_id": passage_id,
            "retrieval_score": round(retrieval_score, 2),
            "active_topic": session.active_topic,
        }
