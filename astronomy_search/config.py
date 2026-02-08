from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    # Repo root is current working directory when running scripts from root.
    return Path(__file__).resolve().parents[1]


def store_dir() -> Path:
    """
    Large offline artifacts live here (ignored by git):
      - downloaded Wikipedia pages (jsonl)
      - sqlite full-text index
      - semantic vector index
      - cached embedding model
    """
    base = os.environ.get("ASTRO_WIKIQA_DIR")
    if base:
        return Path(base).expanduser().resolve()
    return repo_root() / "astronomy_search_store"


def corpus_dir() -> Path:
    return store_dir() / "corpus"


def index_dir() -> Path:
    return store_dir() / "index"


def model_dir() -> Path:
    # Keep model files in-repo store so the app can run offline.
    return store_dir() / "models"


def pages_jsonl_path() -> Path:
    return corpus_dir() / "wikipedia_astronomy_pages.jsonl"


def sqlite_path() -> Path:
    return index_dir() / "chunks.sqlite3"


def hnsw_index_path() -> Path:
    return index_dir() / "chunks_hnsw.bin"


def embeddings_path() -> Path:
    """
    Semantic backend that works without a compiler:
    a normalized float32 embedding matrix saved to disk.
    Shape: (n_chunks, dim), where row index == chunk id.
    """
    return index_dir() / "chunks_embeddings.npy"


def index_meta_path() -> Path:
    return index_dir() / "index_meta.json"

