from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from astronomy_search import config


@dataclass(frozen=True)
class SearchResult:
    chunk_id: int
    title: str
    url: str
    chunk: str
    score: float
    mode: str  # "semantic" or "keyword"


def _tokenize_query(q: str) -> List[str]:
    # Keep simple, safe tokens for FTS5.
    return [t for t in re.findall(r"[A-Za-z0-9_]{2,}", q or "")][:12]


def _fts_query_string(q: str) -> str:
    toks = _tokenize_query(q)
    if not toks:
        return ""
    # Prefix matching with *; join with AND to reduce noise.
    # Quote tokens to avoid reserved characters.
    return " AND ".join([f'"{t}"*' for t in toks])


class WikiQASearcher:
    def __init__(
        self,
        *,
        sqlite_path: Path,
        hnsw_index_path: Optional[Path] = None,
        embeddings_path: Optional[Path] = None,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.sqlite_path = sqlite_path
        self.hnsw_index_path = hnsw_index_path
        self.embeddings_path = embeddings_path
        self.model_name = model_name

        self._conn: Optional[sqlite3.Connection] = None
        self._hnsw = None
        self._model = None
        self._dim: Optional[int] = None
        self._emb = None  # numpy memmap/ndarray of embeddings

    def _conn_open(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.sqlite_path), check_same_thread=False)
        return self._conn

    def _load_semantic(self) -> bool:
        # Prefer native ANN index if it exists AND deps are available,
        # otherwise use numpy-memmap embeddings backend (no compiler required).
        if self._model is not None and (self._hnsw is not None or self._emb is not None):
            return True

        # Force model cache into repo-local store so offline works.
        config.model_dir().mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(config.model_dir()))

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception:
            return False

        # 1) Try HNSW if present and usable.
        if self.hnsw_index_path and self.hnsw_index_path.exists():
            try:
                import hnswlib  # type: ignore
                import numpy as np  # type: ignore
            except Exception:
                hnswlib = None  # type: ignore

            if hnswlib is not None:
                model = SentenceTransformer(self.model_name)
                probe = model.encode(["dimension probe"], normalize_embeddings=True)
                dim = int(probe.shape[1])
                index = hnswlib.Index(space="cosine", dim=dim)
                index.load_index(str(self.hnsw_index_path))
                index.set_ef(64)
                self._model = model
                self._hnsw = index
                self._dim = dim
                return True

        # 2) Try embeddings matrix backend.
        emb_path = self.embeddings_path or config.embeddings_path()
        if not emb_path.exists():
            return False

        try:
            import numpy as np  # type: ignore
        except Exception:
            return False

        model = SentenceTransformer(self.model_name)
        emb = np.load(str(emb_path), mmap_mode="r")
        # emb shape: (n_chunks, dim)
        if len(getattr(emb, "shape", ())) != 2:
            return False
        self._model = model
        self._emb = emb
        self._dim = int(emb.shape[1])
        return True

    def search(self, query: str, *, top_k: int = 8) -> List[SearchResult]:
        query = (query or "").strip()
        if not query:
            return []

        # Prefer semantic if available, otherwise fallback to keyword.
        if self._load_semantic():
            try:
                return self._search_semantic(query, top_k=top_k)
            except Exception:
                # Hard fallback to keyword on any runtime failure.
                return self._search_keyword(query, top_k=top_k)

        return self._search_keyword(query, top_k=top_k)

    def _search_semantic(self, query: str, *, top_k: int) -> List[SearchResult]:
        import numpy as np  # type: ignore

        assert self._model is not None

        qv = self._model.encode([query], normalize_embeddings=True)
        qv = np.asarray(qv, dtype=np.float32)[0]

        labels: List[int] = []
        scores: List[float] = []

        # If HNSW is available, use it.
        if self._hnsw is not None:
            qv2 = np.asarray([qv], dtype=np.float32)
            lbl, dist = self._hnsw.knn_query(qv2, k=max(1, int(top_k)))
            labels = [int(x) for x in lbl[0].tolist()]
            # cosine distance -> similarity = 1 - dist
            scores = [float(1.0 - float(d)) for d in dist[0].tolist()]
        else:
            # Numpy backend: exact cosine similarity via dot product against normalized embeddings.
            assert self._emb is not None
            emb = self._emb
            n = int(emb.shape[0])
            k = max(1, int(top_k))

            # Compute similarities in blocks to avoid huge transient allocations.
            block = 50_000
            best_ids = np.empty((0,), dtype=np.int64)
            best_scores = np.empty((0,), dtype=np.float32)

            for start in range(0, n, block):
                end = min(n, start + block)
                sims = emb[start:end] @ qv  # (block,)
                # Keep top-k for this block
                if (end - start) > k:
                    idx = np.argpartition(sims, -k)[-k:]
                else:
                    idx = np.arange(end - start)
                cand_scores = sims[idx].astype(np.float32, copy=False)
                cand_ids = (idx + start).astype(np.int64, copy=False)

                best_ids = np.concatenate([best_ids, cand_ids])
                best_scores = np.concatenate([best_scores, cand_scores])

                if best_scores.size > k:
                    keep = np.argpartition(best_scores, -k)[-k:]
                    best_ids = best_ids[keep]
                    best_scores = best_scores[keep]

            # Sort final top-k descending
            order = np.argsort(best_scores)[::-1]
            best_ids = best_ids[order]
            best_scores = best_scores[order]
            labels = [int(x) for x in best_ids.tolist()]
            scores = [float(x) for x in best_scores.tolist()]

        conn = self._conn_open()
        cur = conn.cursor()

        results: List[SearchResult] = []
        for cid, score in zip(labels, scores):
            cur.execute("SELECT title, url, chunk FROM chunks WHERE id = ?;", (int(cid),))
            row = cur.fetchone()
            if not row:
                continue
            title, url, chunk = row
            results.append(
                SearchResult(
                    chunk_id=int(cid),
                    title=str(title or ""),
                    url=str(url or ""),
                    chunk=str(chunk or ""),
                    score=score,
                    mode="semantic",
                )
            )
        return results

    def _search_keyword(self, query: str, *, top_k: int) -> List[SearchResult]:
        qs = _fts_query_string(query)
        if not qs:
            return []

        conn = self._conn_open()
        cur = conn.cursor()

        # bm25: lower is better. Convert to a "higher is better" score.
        cur.execute(
            """
            SELECT c.id, c.title, c.url, c.chunk, bm25(chunks_fts) AS rank
            FROM chunks_fts
            JOIN chunks c ON c.id = chunks_fts.rowid
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?;
            """,
            (qs, int(top_k)),
        )

        out: List[SearchResult] = []
        for cid, title, url, chunk, rank in cur.fetchall():
            # bm25 can be negative; squash to a bounded-ish score.
            r = float(rank)
            score = 1.0 / (1.0 + max(0.0, r))
            out.append(
                SearchResult(
                    chunk_id=int(cid),
                    title=str(title or ""),
                    url=str(url or ""),
                    chunk=str(chunk or ""),
                    score=score,
                    mode="keyword",
                )
            )
        return out

