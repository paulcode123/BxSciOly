from __future__ import annotations

import argparse
from pathlib import Path

from astronomy_search import config
from astronomy_search.indexer import build_semantic_embeddings_memmap, build_sqlite_fts


def main() -> None:
    p = argparse.ArgumentParser(description="Build offline keyword+semantic index for astronomy Wikipedia corpus.")
    p.add_argument("--pages", default=str(config.pages_jsonl_path()), help="Input JSONL of downloaded pages")
    p.add_argument("--sqlite", default=str(config.sqlite_path()), help="Output sqlite path")
    p.add_argument("--embeddings", default=str(config.embeddings_path()), help="Output embeddings .npy path (semantic)")
    p.add_argument("--meta", default=str(config.index_meta_path()), help="Output index metadata json path")
    p.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", help="SentenceTransformers model")
    p.add_argument("--no-semantic", action="store_true", help="Only build SQLite FTS, skip embeddings/vector index")
    p.add_argument("--target-words", type=int, default=260, help="Approx words per chunk")
    p.add_argument("--overlap-words", type=int, default=45, help="Approx overlap words per chunk")
    p.add_argument("--batch-size", type=int, default=64, help="Embedding batch size")
    args = p.parse_args()

    pages = Path(args.pages)
    sqlite_path = Path(args.sqlite)
    embeddings_path = Path(args.embeddings)
    meta_path = Path(args.meta)

    if not pages.exists():
        print(f"[error] Pages JSONL not found: {pages}")
        print("")
        print("Run the downloader first (creates the JSONL corpus):")
        print("  python astronomy_wiki_download.py --max-bytes 1000000000")
        print("")
        print("If you downloaded to a different path, pass it explicitly:")
        print("  python astronomy_wiki_build_index.py --pages <path-to-jsonl>")
        raise SystemExit(2)

    stats = build_sqlite_fts(
        pages_jsonl=pages,
        sqlite_path=sqlite_path,
        target_words=args.target_words,
        overlap_words=args.overlap_words,
    )
    print(f"[build] sqlite+fts pages_read={stats.pages_read:,} chunks_written={stats.chunks_written:,}")

    if not args.no_semantic:
        sem = build_semantic_embeddings_memmap(
            sqlite_path=sqlite_path,
            embeddings_path=embeddings_path,
            meta_path=meta_path,
            model_name=args.model,
            batch_size=args.batch_size,
        )
        print(f"[build] semantic chunks_indexed={sem.chunks_indexed:,} dim={sem.dim} model={sem.model_name}")


if __name__ == "__main__":
    main()

