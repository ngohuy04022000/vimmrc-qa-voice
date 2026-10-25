"""So sánh EmbeddingRetriever (qwen3-embed-vi qua Ollama) với Retriever BM25 đã
tune (OPTIMIZED_CONFIG) trên cùng tập câu hỏi dev. Embedding API chậm hơn BM25
nhiều cấp độ (mạng + model), nên mặc định chỉ lấy mẫu nhỏ --n câu để chạy trong
vài phút; dùng --n lớn hơn nếu cần số liệu chắc hơn và chấp nhận chờ lâu hơn.

Chạy:
    python benchmark_embedding_vs_bm25.py --n 100
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_retrieval import measure
from embedding_retriever import EmbeddingRetriever
from retrieval_client import OPTIMIZED_CONFIG, Retriever
from retrieval_cli import read_json, vimmrc_passages, vimmrc_queries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", default="../data/dev_vimmrc.json")
    parser.add_argument("--embedding-index", default="../data/embedding_index.npz",
                        help="Đã build bằng embedding_retriever.EmbeddingRetriever.save()")
    parser.add_argument("--n", type=int, default=100, help="Số câu hỏi lấy mẫu để đo embedding (chậm)")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "sentence_transformers"])
    parser.add_argument("--model-name", default=None,
                        help="Chỉ áp dụng với --backend sentence_transformers; mặc định intfloat/multilingual-e5-base")
    args = parser.parse_args(argv)

    dev_records = read_json(args.dev)
    passages = vimmrc_passages(dev_records, "dev")
    queries = vimmrc_queries(dev_records, "dev", corpus_passages=passages)[:args.n]
    print(f"Đo trên {len(queries)} câu hỏi, corpus {len(passages)} đoạn văn (chỉ dev, tách riêng mỗi lần)")

    bm25 = Retriever(passages, **OPTIMIZED_CONFIG)
    bm25_metrics = measure(bm25, queries)
    print("BM25 (OPTIMIZED_CONFIG):", bm25_metrics)

    t0 = time.perf_counter()
    embed_retriever = EmbeddingRetriever(passages, backend=args.backend, model_name=args.model_name)  # embed riêng cho dev
    print(f"Embed {len(passages)} đoạn văn dev ({args.backend}, {embed_retriever.model_name}): "
          f"{time.perf_counter()-t0:.1f}s")
    embed_metrics = measure(embed_retriever, queries)
    print(f"Embedding ({embed_retriever.model_name}):", embed_metrics)


if __name__ == "__main__":
    main()
