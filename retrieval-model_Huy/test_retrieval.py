"""Behavioral tests for ranking, persistence, corpus preparation and metrics."""

import json
from pathlib import Path
import tempfile
import unittest

from retrieval_client import BASELINE_CONFIG, OPTIMIZED_CONFIG, Retriever
from retrieval_cli import evaluate, vimmrc_passages, vimmrc_queries


ROOT = Path(__file__).parent


class RetrieverTests(unittest.TestCase):
    def setUp(self):
        self.passages = json.loads((ROOT / "synthetic_passages.json").read_text(encoding="utf-8"))
        self.retriever = Retriever(self.passages)

    def test_retrieve_ranks_relevant_passage(self):
        hits = self.retriever.search("Hành tinh nào gần MẶT TRỜI nhất?", top_k=2)
        self.assertEqual(hits[0]["id"], "mercury")
        self.assertGreater(hits[0]["score"], hits[1]["score"])
        self.assertEqual(self.retriever.retrieve("Hành tinh nào gần Mặt Trời nhất?"), self.passages[1]["passage"])

    def test_missing_and_empty_queries(self):
        self.assertEqual(self.retriever.search(""), [])
        self.assertEqual(self.retriever.retrieve("không-trùng-khớp"), "")
        self.assertEqual(Retriever([]).search("Mặt Trời"), [])

    def test_unicode_normalization_and_save_load(self):
        decomposed = "Ma\u0323\u0306t Trơ\u0300i"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifacts" / "index.json"
            self.retriever.save(path)
            self.assertTrue(path.exists())
            loaded = Retriever.load(path)
            self.assertEqual(loaded.passages, self.passages)
            self.assertEqual((loaded.k1, loaded.b, loaded.query_stopwords, loaded.bigram_boost),
                             (2.1, 1.0, True, 0.4))
            self.assertEqual(loaded.search(decomposed, 1)[0]["id"], "sun")

    def test_default_tuned_and_explicit_baseline_config(self):
        self.assertEqual((self.retriever.k1, self.retriever.b, self.retriever.query_stopwords,
                          self.retriever.bigram_boost), tuple(OPTIMIZED_CONFIG.values()))
        baseline = Retriever(self.passages, **BASELINE_CONFIG)
        self.assertEqual((baseline.k1, baseline.b, baseline.query_stopwords,
                          baseline.bigram_boost), tuple(BASELINE_CONFIG.values()))

    def test_bigram_boost_rewards_matching_phrase(self):
        passages = [{"id": "one", "passage": "mèo đen đuổi chuột"},
                    {"id": "two", "passage": "đen mèo đuổi chuột"}]
        retriever = Retriever(passages, query_stopwords=False, bigram_boost=2.0)
        self.assertEqual(retriever.search("mèo đen", 1)[0]["id"], "one")

    def test_stopword_only_query_falls_back_to_original_terms(self):
        self.assertTrue(Retriever([{"id": "x", "passage": "Nó là ai?"}]).search("là"))

    def test_load_legacy_index_defaults_to_optimized_config(self):
        # Index JSON cũ chỉ lưu k1/b, thiếu query_stopwords/bigram_boost: các trường thiếu
        # phải lấy mặc định từ OPTIMIZED_CONFIG (khớp với Retriever(passages)), không phải
        # baseline cũ, để load() và khởi tạo mới không lặng lẽ cho kết quả khác nhau.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old_index.json"
            path.write_text(json.dumps({"passages": self.passages, "k1": 1.5, "b": 0.75}), encoding="utf-8")
            loaded = Retriever.load(path)
            self.assertEqual(
                (loaded.k1, loaded.b, loaded.query_stopwords, loaded.bigram_boost),
                (1.5, 0.75, OPTIMIZED_CONFIG["query_stopwords"], OPTIMIZED_CONFIG["bigram_boost"]),
            )

    def test_load_index_missing_all_bm25_fields_uses_optimized_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bare_index.json"
            path.write_text(json.dumps({"passages": self.passages}), encoding="utf-8")
            loaded = Retriever.load(path)
            self.assertEqual((loaded.k1, loaded.b, loaded.query_stopwords, loaded.bigram_boost),
                             tuple(OPTIMIZED_CONFIG.values()))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            Retriever([self.passages[0], self.passages[0]])
        with self.assertRaises(ValueError):
            Retriever([{"id": "punctuation", "passage": "..."}])
        with self.assertRaises(ValueError):
            self.retriever.search("Mặt Trời", top_k=0)

    def test_evaluation_uses_passage_ids(self):
        queries = json.loads((ROOT / "synthetic_queries.json").read_text(encoding="utf-8"))
        metrics = evaluate(self.retriever, queries, 1)
        self.assertEqual(metrics["recall@1"], 1.0)
        self.assertEqual(metrics["mrr@1"], 1.0)
        self.assertEqual(metrics["corpus_coverage"], 1.0)

    def test_vimmrc_extraction_excludes_labels(self):
        records = [{"article": "Đoạn văn gốc", "questions": ["Câu hỏi?"], "options": [["đáp án"]], "answers": ["A"]}]
        passages = vimmrc_passages(records, "dev")
        self.assertEqual(passages, [{"id": "dev:0000", "passage": "Đoạn văn gốc"}])
        self.assertEqual(vimmrc_queries(records, "dev"), [{"question": "Câu hỏi?", "relevant_ids": ["dev:0000"]}])
        metrics = evaluate(Retriever(passages), vimmrc_queries(records, "dev"), 1)
        self.assertEqual(metrics["corpus_coverage"], 1.0)

    def test_missing_gold_id_is_counted_as_uncovered(self):
        metrics = evaluate(self.retriever, [{"question": "Sao Thủy?", "relevant_ids": ["dev:0000"]}], 1)
        self.assertEqual(metrics["corpus_coverage"], 0.0)
        self.assertEqual(metrics["recall@1"], 0.0)

    def test_vimmrc_cross_split_exact_article_match(self):
        record = {"article": "Cùng một bài đọc", "questions": ["Bài đọc nào?"]}
        train_passages = vimmrc_passages([record], "train")
        queries = vimmrc_queries([record], "dev", train_passages)
        self.assertEqual(queries[0]["relevant_ids"], ["train:0000"])
        self.assertEqual(evaluate(Retriever(train_passages), queries, 1)["corpus_coverage"], 1.0)

    def test_vimmrc_same_prefix_different_article_is_uncovered(self):
        record = {"article": "Mặt Trời có ánh sáng", "questions": ["Mặt Trời là gì?"]}
        corpus = [{"id": "dev:0000", "passage": "Mặt Trời là một ngôi sao"}]
        queries = vimmrc_queries([record], "dev", corpus)
        self.assertNotIn(queries[0]["relevant_ids"][0], {item["id"] for item in corpus})
        metrics = evaluate(Retriever(corpus), queries, 1)
        self.assertEqual(metrics["corpus_coverage"], 0.0)
        self.assertEqual(metrics["recall@1"], 0.0)

    def test_vimmrc_match_normalizes_unicode_and_whitespace(self):
        record = {"article": "Mặt   Trời\nchiếu sáng", "questions": ["Trời làm gì?"]}
        corpus = [{"id": "train:0000", "passage": "Ma\u0323\u0306t Trời chiếu sáng"}]
        queries = vimmrc_queries([record], "dev", corpus)
        self.assertEqual(queries[0]["relevant_ids"], ["train:0000"])


class RerankTests(unittest.TestCase):
    def test_quantize_reranker_swaps_linear_layers_in_place(self):
        import torch
        from kb_retriever import quantize_reranker

        class Fake:
            model = torch.nn.Sequential(torch.nn.Linear(8, 8), torch.nn.ReLU(), torch.nn.Linear(8, 1))

        fake, before = Fake(), None
        before = fake.model(torch.ones(2, 8)).detach()
        self.assertTrue(quantize_reranker(fake))
        self.assertIn("quantized", type(fake.model[0]).__module__)
        self.assertTrue(torch.allclose(fake.model(torch.ones(2, 8)), before, atol=0.1))
        self.assertFalse(quantize_reranker(object()))  # no .model: falls back instead of raising

    def test_tier1_bonus_does_not_beat_saturated_wiki_score(self):
        from kb_retriever import TieredRetriever

        class Fixed:
            def __init__(self, hits): self.hits, self.passages = hits, hits
            def search(self, q, k): return self.hits[:k]

        class CE:
            def predict(self, pairs, batch_size=16):
                return [0.9999 if "Thủy" in p else 0.86 if "Hải" in p else 0.3 for _, p in pairs]

        kb = Fixed([{"id": "kb:1", "passage": "Sao Hải Vương xa Mặt Trời nhất.", "score": 9.0},
                    {"id": "kb:2", "passage": "Sao Hỏa màu đỏ.", "score": 5.0}])
        wiki = Fixed([{"id": "w:1", "passage": "Sao Thủy gần Mặt Trời nhất.", "score": 3.0}])
        hits = TieredRetriever(kb, wiki, reranker=CE()).search("Hành tinh nào gần Mặt Trời nhất?", 3)
        self.assertEqual([h["id"] for h in hits], ["w:1", "kb:1", "kb:2"])


if __name__ == "__main__":
    unittest.main()
