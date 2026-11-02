"""Unit and regression tests for Out-of-Dataset 100+ Benchmark Suite."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
for folder in ("scripts", "retrieval-model_Huy", "mrc-model_Huy"):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from intent_router import ConversationalIntentRouter, polish_answer, rerank_hits
from qa_pipeline import QAPipeline
from mrc_client import LexicalBaselineClient
from retrieval_client import Retriever


class OutOfDatasetSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite_path = ROOT / "data" / "out_of_dataset_eval_100.json"
        with open(cls.suite_path, "r", encoding="utf-8") as f:
            cls.items = json.load(f)

    def test_item_count_exceeds_100(self):
        self.assertGreaterEqual(len(self.items), 100, "Suite must contain at least 100 items")
        self.assertEqual(len(self.items), 110, "Expected 110 curated items")

    def test_schema_validity(self):
        required_keys = {"id", "category", "type", "question", "reference_answer"}
        for item in self.items:
            self.assertTrue(required_keys.issubset(item.keys()), f"Item {item.get('id')} missing keys")
            self.assertTrue(item["question"].strip(), f"Item {item.get('id')} has empty question")
            self.assertTrue(item["reference_answer"].strip(), f"Item {item.get('id')} has empty reference_answer")
            self.assertIn(item["type"], ("conversation", "factual"))

    def test_zero_data_leakage_with_vimmrc(self):
        data_dir = ROOT / "data"
        split_files = ["train_vimmrc.json", "dev_vimmrc.json", "test_vimmrc.json"]
        vimmrc_questions = set()

        for filename in split_files:
            file_path = data_dir / filename
            if not file_path.exists():
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = data.get("data", data) if isinstance(data, dict) else data
            for rec in records:
                qs = rec.get("questions", [])
                if isinstance(qs, list):
                    for q in qs:
                        if isinstance(q, str) and q.strip():
                            vimmrc_questions.add(q.strip().lower())
                elif isinstance(rec.get("question"), str):
                    vimmrc_questions.add(rec["question"].strip().lower())

        self.assertGreater(len(vimmrc_questions), 0, "ViMMRC dataset questions should be loaded")

        leaked = []
        for item in self.items:
            q = item["question"].strip().lower()
            if q in vimmrc_questions:
                leaked.append(item["id"])

        self.assertEqual(len(leaked), 0, f"Detected {len(leaked)} leaked questions from ViMMRC: {leaked}")

    def test_all_conversational_items_match_intent_router(self):
        conv_items = [item for item in self.items if item["type"] == "conversation"]
        self.assertEqual(len(conv_items), 25)

        for item in conv_items:
            q = item["question"]
            ans = ConversationalIntentRouter.get_conversational_response(q)
            self.assertIsNotNone(
                ans,
                f"Conversational question failed intent routing: ID={item['id']} Q='{q}'"
            )
            self.assertTrue(len(ans) > 10)

    def test_pipeline_smoke_with_lexical_reader(self):
        retriever = Retriever([
            {
                "id": "doc:thanglong",
                "passage": "Năm 1010 vua Lý Thái Tổ dời đô từ Hoa Lư về Đại La và đổi tên thành Thăng Long, nay là Hà Nội.",
            }
        ])
        reader = LexicalBaselineClient()
        pipeline = QAPipeline(retriever, reader)

        # Conversational query
        conv_res = pipeline.predict("Xin chào trợ lý!")
        self.assertTrue(conv_res["is_conversational"])
        self.assertIn("Xin chào", conv_res["answer"])

        # Factual query
        fact_res = pipeline.predict("Vua Lý Thái Tổ dời đô về đâu vào năm 1010?")
        self.assertFalse(fact_res["is_conversational"])
        self.assertTrue(len(fact_res["answer"]) > 0)


if __name__ == "__main__":
    unittest.main()
