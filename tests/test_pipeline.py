import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qa_pipeline import QAPipeline, Retriever, LexicalBaselineClient


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = QAPipeline(Retriever([
            {"id": "hanoi", "passage": "Hà Nội là thủ đô của Việt Nam."},
            {"id": "coffee", "passage": "Cà phê được trồng ở Tây Nguyên."},
        ]), LexicalBaselineClient())

    def test_real_modules_connect_and_return_text(self):
        result = self.pipeline.predict("Thủ đô Việt Nam ở đâu?")
        self.assertEqual(result["passage_id"], "hanoi")
        self.assertIn("Hà Nội", result["answer"])
        self.assertIsInstance(self.pipeline.answer_question("Thủ đô Việt Nam?"), str)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            self.pipeline.predict("  ")

    def test_no_match_does_not_call_reader(self):
        class FailingReader:
            def answer_question(self, *args):
                raise AssertionError("Reader must not run without evidence")
        self.pipeline.reader = FailingReader()
        result = self.pipeline.predict("zzzzqqqq")
        self.assertIsNone(result["passage_id"])
        self.assertEqual(result["retrieval_score"], 0)

    def test_multiple_choice_contract_and_question_only_retrieval(self):
        calls = []
        class TrackingRetriever:
            def search(self, question, top_k):
                calls.append(question)
                return [{"id": "p", "passage": "Hà Nội là thủ đô Việt Nam.", "score": 1.0}]
        class ChoiceReader:
            def predict(self, question, passage, options):
                return {"label": "B", "answer": options[1], "scores": {"B": 0.8}}
        pipeline = QAPipeline(TrackingRetriever(), ChoiceReader())
        result = pipeline.predict("Thủ đô?", ["Huế", "Hà Nội", "Đà Nẵng", "Cần Thơ"])
        self.assertEqual(calls, ["Thủ đô?"])
        self.assertEqual(result["choice_label"], "B")
        self.assertEqual(result["answer"], "Hà Nội")

    def test_invalid_choices(self):
        with self.assertRaises(ValueError):
            self.pipeline.predict("question", ["", "", "", ""])


if __name__ == "__main__":
    unittest.main()
