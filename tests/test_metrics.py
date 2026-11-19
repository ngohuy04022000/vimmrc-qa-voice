"""Test cho scripts/metrics.py, bootstrap_ci.paired_bootstrap và simulate_gate.simulate (không nạp mô hình)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bootstrap_ci import paired_bootstrap  # noqa: E402
from metrics import best_f1, token_f1_multiset, token_f1_set_noaccent  # noqa: E402
from simulate_gate import simulate  # noqa: E402


def test_multiset_counts_repeats_and_keeps_accents():
    # đếm lặp: "a a" so với "a" -> common=1, 2*1/(2+1)
    assert token_f1_multiset("a a", "a") == pytest.approx(2 / 3)
    # giữ dấu: "ma" khác "má"
    assert token_f1_multiset("má", "ma") == 0.0
    assert token_f1_multiset("Hà Nội.", "hà nội") == 1.0  # hạ chữ, bỏ dấu câu


def test_set_noaccent_is_the_legacy_non_standard_metric():
    assert token_f1_set_noaccent("má", "ma") == 1.0          # bỏ dấu nên coi là trùng
    # giao của TẬP chia cho độ dài DANH SÁCH: "a a" so với "a" cho precision 1/2, recall 1 -> 2/3 giống multiset ở ca này
    assert token_f1_set_noaccent("a a b", "a") == pytest.approx(2 * (1 / 3) * 1 / (1 / 3 + 1))
    assert token_f1_set_noaccent("", "a") == 0.0


def test_best_f1_takes_max_over_references():
    assert best_f1("hà nội", ["huế", "hà nội"]) == 1.0
    assert best_f1("hà nội", ["huế"]) == 0.0


def test_paired_bootstrap_identical_and_shifted():
    same = paired_bootstrap([0.5] * 20, [0.5] * 20, n=200)
    assert same["diff"] == 0 and same["ci95"] == [0, 0] and not same["significant_at_95"]
    up = paired_bootstrap([1.0] * 30, [0.0] * 30, n=200)
    assert up["diff"] == 1.0 and up["significant_at_95"] and up["p_diff_le_0"] == 0
    # cùng seed -> tái lập được
    assert paired_bootstrap([0, 1, 1, 0, 1], [0, 0, 1, 0, 0], n=200, seed=3) == paired_bootstrap([0, 1, 1, 0, 1], [0, 0, 1, 0, 0], n=200, seed=3)
    with pytest.raises(AssertionError):
        paired_bootstrap([1.0], [], n=10)


def test_simulate_gate_replays_threshold_on_qa_rows_only():
    cfg = {
        "answerable": [
            {"q": "q1", "src": "ood", "kind": "qa", "rerank_score": 0.2, "full_answer": "x", "answer": "x"},
            {"q": "q2", "src": "ood", "kind": "qa", "rerank_score": 4.0, "full_answer": "hà nội", "answer": "hà nội"},
            {"q": "q3", "src": "test", "kind": "compare", "rerank_score": None, "full_answer": "y", "answer": "y"},
            {"q": "q4", "src": "test", "kind": "unknown", "rerank_score": None, "full_answer": "xin lỗi", "answer": "xin lỗi"},
        ],
        "unanswerable": [{"q": "u1", "kind": "qa", "rerank_score": 0.5, "answer": "z"},
                         {"q": "u2", "kind": "qa", "rerank_score": 3.0, "answer": "z"}],
    }
    refs = {q: ["hà nội"] for q in ("q1", "q2", "q3", "q4")}
    none = simulate(cfg, refs, None)
    assert none["false_refusal"] == "1/4" and none["correct_refusal"] == "0/2"      # chỉ hàng kind=unknown
    gate1 = simulate(cfg, refs, 1.0)
    assert gate1["false_refusal"] == "2/4"            # q1 (điểm 0,2 < 1) bị cổng chặn; q3 (compare) không bị cổng áp dụng
    assert gate1["correct_refusal"] == "1/2"          # u1 bị chặn, u2 (điểm 3,0) không
    assert simulate(cfg, refs, 5.0)["false_refusal"] == "3/4"  # ngưỡng cao chặn thêm q2
    assert gate1["f1_all"] >= 0.25 - 1e-9              # q2 đúng -> F1 trung bình tối thiểu 1/4
