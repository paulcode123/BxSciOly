from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, render_template, request

try:
    from astronomy_search import config
    from astronomy_search.search_engine import WikiQASearcher
    ASTRONOMY_SEARCH_AVAILABLE = True
except ImportError:
    ASTRONOMY_SEARCH_AVAILABLE = False
    config = None
    WikiQASearcher = None


wikiqa_routes = Blueprint("wikiqa_routes", __name__)

_searcher: Optional[Any] = None


def _get_searcher() -> Any:
    global _searcher
    if not ASTRONOMY_SEARCH_AVAILABLE:
        raise ImportError("astronomy_search module is not available")
    if _searcher is None:
        _searcher = WikiQASearcher(
            sqlite_path=config.sqlite_path(),
            hnsw_index_path=config.hnsw_index_path(),
            embeddings_path=config.embeddings_path(),
        )
    return _searcher


def _index_status() -> Dict[str, Any]:
    if not ASTRONOMY_SEARCH_AVAILABLE:
        return {
            "pages_jsonl": "",
            "sqlite": "",
            "hnsw": "",
            "embeddings": "",
            "pages_ok": False,
            "sqlite_ok": False,
            "semantic_ok": False,
            "semantic_backend": "none",
        }
    sqlite_ok = config.sqlite_path().exists()
    hnsw_ok = config.hnsw_index_path().exists()
    emb_ok = config.embeddings_path().exists()
    pages_ok = config.pages_jsonl_path().exists()
    return {
        "pages_jsonl": str(config.pages_jsonl_path()),
        "sqlite": str(config.sqlite_path()),
        "hnsw": str(config.hnsw_index_path()),
        "embeddings": str(config.embeddings_path()),
        "pages_ok": pages_ok,
        "sqlite_ok": sqlite_ok,
        "semantic_ok": bool(hnsw_ok or emb_ok),
        "semantic_backend": "hnsw" if hnsw_ok else ("embeddings" if emb_ok else "none"),
    }


@wikiqa_routes.route("/user/wikiqa", methods=["GET"])
def user_wikiqa() -> str:
    q = (request.args.get("q") or "").strip()
    top_k = int(request.args.get("k") or 8)

    status = _index_status()
    results = []
    error: Optional[str] = None

    if q and status["sqlite_ok"]:
        try:
            results = _get_searcher().search(q, top_k=top_k)
        except Exception as e:
            error = str(e)

    return render_template(
        "user/wikiqa.html",
        q=q,
        results=results,
        top_k=top_k,
        status=status,
        error=error,
    )


@wikiqa_routes.route("/api/wikiqa/search", methods=["GET"])
def api_wikiqa_search():
    q = (request.args.get("q") or "").strip()
    top_k = int(request.args.get("k") or 8)

    status = _index_status()
    if not q:
        return jsonify({"ok": True, "query": q, "results": [], "status": status})

    if not status["sqlite_ok"]:
        return jsonify(
            {
                "ok": False,
                "error": "index_not_built",
                "message": "SQLite index not found. Run astronomy_wiki_build_index.py first.",
                "status": status,
            }
        ), 400

    try:
        results = _get_searcher().search(q, top_k=top_k)
        return jsonify(
            {
                "ok": True,
                "query": q,
                "results": [
                    {
                        "chunk_id": r.chunk_id,
                        "title": r.title,
                        "url": r.url,
                        "chunk": r.chunk,
                        "score": r.score,
                        "mode": r.mode,
                    }
                    for r in results
                ],
                "status": status,
            }
        )
    except Exception as e:
        return jsonify({"ok": False, "error": "search_failed", "message": str(e), "status": status}), 500

