from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from astronomy_search import config


def _iter_pages_jsonl(path: Path) -> Iterator[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _word_chunks(text: str, *, target_words: int = 260, overlap_words: int = 45) -> List[str]:
    """
    Chunk by words with overlap, but try to respect paragraph boundaries.
    """
    text = (text or "").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    words_by_para = [p.split() for p in paragraphs]

    chunks: List[str] = []
    buf: List[str] = []

    def flush_buf() -> None:
        nonlocal buf
        if not buf:
            return
        chunk = " ".join(buf).strip()
        if chunk:
            chunks.append(chunk)
        # keep overlap
        if overlap_words > 0 and len(buf) > overlap_words:
            buf = buf[-overlap_words:]
        else:
            buf = []

    for wpara in words_by_para:
        if not wpara:
            continue
        # If a single paragraph is huge, stream it in.
        for w in wpara:
            buf.append(w)
            if len(buf) >= target_words:
                flush_buf()
        # Paragraph boundary: add a little separation without forcing flush.
        buf.append("\n")

    # Final flush: remove stray newlines inside
    buf = [w for w in buf if w != "\n"]
    flush_buf()

    # Post-clean: normalize whitespace.
    cleaned = []
    for c in chunks:
        c = re.sub(r"\s+", " ", c).strip()
        if len(c) >= 200:
            cleaned.append(c)
    return cleaned


@dataclass(frozen=True)
class BuildStats:
    pages_read: int
    chunks_written: int


def _ensure_sqlite(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    return conn


def build_sqlite_fts(
    *,
    pages_jsonl: Path,
    sqlite_path: Path,
    target_words: int = 260,
    overlap_words: int = 45,
) -> BuildStats:
    conn = _ensure_sqlite(sqlite_path)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS chunks (
          id INTEGER PRIMARY KEY,
          pageid INTEGER,
          title TEXT,
          url TEXT,
          chunk TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
        USING fts5(chunk, title, content='chunks', content_rowid='id');
        """
    )

    # If re-running, clear existing rows to keep rowids aligned with vector index.
    cur.execute("DELETE FROM chunks;")
    cur.execute("DELETE FROM chunks_fts;")
    conn.commit()

    pages_read = 0
    chunks_written = 0

    insert_chunk = "INSERT INTO chunks(id, pageid, title, url, chunk) VALUES (?, ?, ?, ?, ?);"
    insert_fts = "INSERT INTO chunks_fts(rowid, chunk, title) VALUES (?, ?, ?);"

    next_id = 0
    for page in _iter_pages_jsonl(pages_jsonl):
        pages_read += 1
        pageid = page.get("pageid")
        title = str(page.get("title") or "")
        url = str(page.get("url") or "")
        extract = str(page.get("extract") or "")
        if not extract:
            continue

        for chunk in _word_chunks(extract, target_words=target_words, overlap_words=overlap_words):
            cid = next_id
            next_id += 1
            cur.execute(insert_chunk, (cid, pageid, title, url, chunk))
            cur.execute(insert_fts, (cid, chunk, title))
            chunks_written += 1

        if pages_read % 200 == 0:
            conn.commit()

    conn.commit()
    conn.close()
    return BuildStats(pages_read=pages_read, chunks_written=chunks_written)


@dataclass(frozen=True)
class SemanticBuildStats:
    chunks_indexed: int
    dim: int
    model_name: str


def build_semantic_embeddings_memmap(
    *,
    sqlite_path: Path,
    embeddings_path: Path,
    meta_path: Path,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 64,
) -> SemanticBuildStats:
    """
    Build a semantic index without native compilation on Windows:
    - Save a normalized float32 embedding matrix to `embeddings_path` as .npy
    - Store metadata in `meta_path`

    Search later does dot-product (cosine similarity since vectors are normalized).

    This downloads the embedding model on first run; afterwards, it works offline.
    """
    embeddings_path.parent.mkdir(parents=True, exist_ok=True)

    import numpy as np

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Missing dependency 'sentence-transformers'. Install it to build semantic index."
        ) from e

    # Force model cache into repo-local store so offline works consistently.
    config.model_dir().mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(config.model_dir()))

    model = SentenceTransformer(model_name)

    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM chunks;")
    (n_chunks,) = cur.fetchone() or (0,)
    if not n_chunks:
        raise RuntimeError("No chunks found in sqlite. Run build_sqlite_fts first.")

    probe = model.encode(["dimension probe"], normalize_embeddings=True)
    dim = int(probe.shape[1])

    # Pre-allocate full embedding matrix on disk.
    tmp_path = embeddings_path.with_suffix(embeddings_path.suffix + ".tmp")
    emb_matrix = np.memmap(
        str(tmp_path),
        dtype=np.float32,
        mode="w+",
        shape=(int(n_chunks), int(dim)),
    )

    cur.execute("SELECT id, chunk FROM chunks ORDER BY id ASC;")
    ids_batch: List[int] = []
    texts_batch: List[str] = []
    total_indexed = 0

    def flush() -> None:
        nonlocal total_indexed, ids_batch, texts_batch
        if not ids_batch:
            return
        emb = model.encode(texts_batch, normalize_embeddings=True, batch_size=batch_size)
        emb = np.asarray(emb, dtype=np.float32)
        for i, cid in enumerate(ids_batch):
            emb_matrix[int(cid), :] = emb[i, :]
        total_indexed += len(ids_batch)
        ids_batch = []
        texts_batch = []

    for row in cur:
        cid = int(row[0])
        text = str(row[1] or "")
        ids_batch.append(cid)
        texts_batch.append(text)
        if len(ids_batch) >= batch_size:
            flush()
            if total_indexed % 5000 == 0:
                print(f"[index] embedded {total_indexed:,}/{n_chunks:,}")

    flush()
    conn.close()

    # Persist as .npy for convenient mmap loading later.
    emb_matrix.flush()
    np.save(str(embeddings_path), np.asarray(emb_matrix))
    try:
        os.remove(str(tmp_path))
    except Exception:
        pass

    meta = {
        "created_at_unix": int(time.time()),
        "model_name": model_name,
        "dim": dim,
        "chunks_indexed": total_indexed,
        "backend": "numpy_memmap",
        "embeddings_path": str(embeddings_path),
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return SemanticBuildStats(chunks_indexed=total_indexed, dim=dim, model_name=model_name)


def build_semantic_hnsw(
    *,
    sqlite_path: Path,
    index_path: Path,
    meta_path: Path,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 64,
) -> SemanticBuildStats:
    """
    Build an on-disk HNSW index over all chunks (id == rowid).

    This downloads the embedding model on first run; afterwards, it works offline.
    """
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Lazy imports so the web app can still run keyword-only without these deps installed.
    import numpy as np

    try:
        import hnswlib  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Missing dependency 'hnswlib'. Install it to build semantic index."
        ) from e

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Missing dependency 'sentence-transformers'. Install it to build semantic index."
        ) from e

    # Force model cache into repo-local store so offline works consistently.
    config.model_dir().mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(config.model_dir()))

    model = SentenceTransformer(model_name)

    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM chunks;")
    (n_chunks,) = cur.fetchone() or (0,)
    if not n_chunks:
        raise RuntimeError("No chunks found in sqlite. Run build_sqlite_fts first.")

    # Determine embedding dimension.
    test_vec = model.encode(["dimension probe"], normalize_embeddings=True)
    dim = int(test_vec.shape[1])

    index = hnswlib.Index(space="cosine", dim=dim)
    index.init_index(max_elements=int(n_chunks), ef_construction=200, M=32)
    index.set_ef(64)

    # Stream chunks and embed.
    cur.execute("SELECT id, chunk FROM chunks ORDER BY id ASC;")

    ids_batch: List[int] = []
    texts_batch: List[str] = []
    total_indexed = 0

    def flush() -> None:
        nonlocal total_indexed, ids_batch, texts_batch
        if not ids_batch:
            return
        emb = model.encode(texts_batch, normalize_embeddings=True, batch_size=batch_size)
        emb = np.asarray(emb, dtype=np.float32)
        index.add_items(emb, np.asarray(ids_batch, dtype=np.int64))
        total_indexed += len(ids_batch)
        ids_batch = []
        texts_batch = []

    for row in cur:
        cid = int(row[0])
        text = str(row[1] or "")
        ids_batch.append(cid)
        texts_batch.append(text)
        if len(ids_batch) >= batch_size:
            flush()
            if total_indexed % 5000 == 0:
                # Basic progress signal for long runs.
                print(f"[index] embedded {total_indexed:,}/{n_chunks:,}")

    flush()
    conn.close()

    index.save_index(str(index_path))

    meta = {
        "created_at_unix": int(time.time()),
        "model_name": model_name,
        "dim": dim,
        "chunks_indexed": total_indexed,
        "space": "cosine",
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return SemanticBuildStats(chunks_indexed=total_indexed, dim=dim, model_name=model_name)

