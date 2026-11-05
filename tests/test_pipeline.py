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

    def test_reader_gets_question_and_retrieved_passage(self):
        calls = []
        class TrackingRetriever:
            def search(self, question, top_k):
                calls.append(question)
                return [{"id": "p", "passage": "Hà Nội là thủ đô Việt Nam.", "score": 1.0}]
        class EchoReader:
            def answer_question(self, question, passage):
                return passage
        result = QAPipeline(TrackingRetriever(), EchoReader()).predict("Thủ đô?")
        self.assertEqual(calls, ["Thủ đô?"])
        self.assertEqual(result["answer"], "Hà Nội là thủ đô Việt Nam.")


if __name__ == "__main__":
    unittest.main()
