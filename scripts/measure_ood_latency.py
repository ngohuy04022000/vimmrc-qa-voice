"""Do do tre /api/ask tren bo 110 cau ngoai dataset qua Docker dang chay (cau hinh trien khai)."""
import json, statistics as st, sys, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8090"
items = json.load(open(ROOT / "data" / "out_of_dataset_eval_100.json", encoding="utf-8"))
def ask(q, sid):
    req = urllib.request.Request(URL + "/api/ask", json.dumps({"question": q, "session_id": sid}).encode(), {"Content-Type": "application/json"})
    t = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as r: d = json.load(r)
    return (time.perf_counter() - t) * 1000, d
ask("Hà Nội là thủ đô của nước nào?", "warm")  # nap mo hinh
rows = []
for it in items:
    ms, d = ask(it["question"], "ood-" + it["id"])
    ans = (d.get("answer") or "").strip()
    rows.append({"id": it["id"], "category": it["category"], "ms": round(ms, 1), "complete": bool(ans)})
cats = {}
for r in rows: cats.setdefault(r["category"], []).append(r)
out = {"what": "do tre /api/ask Docker CPU 4 luong, cau hinh trien khai (vi-mrc-large, reranker INT8, DIALOGUE_DETAIL theo env), 110 cau",
       "total": len(rows), "complete_pct": round(100 * sum(r["complete"] for r in rows) / len(rows), 1),
       "mean_ms": round(st.mean(r["ms"] for r in rows), 1), "median_ms": round(st.median(r["ms"] for r in rows), 1),
       "by_category": {c: {"n": len(v), "mean_ms": round(st.mean(x["ms"] for x in v), 1), "median_ms": round(st.median(x["ms"] for x in v), 1)} for c, v in cats.items()},
       "rows": rows}
json.dump(out, open(ROOT / "reports" / "ood_latency_docker.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))
