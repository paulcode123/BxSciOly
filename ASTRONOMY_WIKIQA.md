# Offline Astronomy Wikipedia Q&A (WikiQA)

This adds an **offline** search page to the site: `GET /user/wikiqa`.

It works in two layers:
- **Keyword search (SQLite FTS5)**: lightweight and always available once you build the SQLite index.
- **Semantic search (optional)**: higher quality for natural-language questions, using `sentence-transformers` + a **numpy embeddings matrix** (no compiler required on Windows).

All large artifacts are stored in `astronomy_search_store/` (ignored by git).

## 1) Install dependencies

From repo root:

```bash
pip install -r requirements.txt
```

If you only want keyword search, you can skip the semantic deps by not installing them and building with `--no-semantic` (below).

## 2) Download ~1GB of astronomy Wikipedia pages (plaintext)

```bash
python astronomy_wiki_download.py --max-bytes 1000000000
```

Output file (default):
- `astronomy_search_store/corpus/wikipedia_astronomy_pages.jsonl`

## 3) Build the offline index

### Keyword-only (fastest)

```bash
python astronomy_wiki_build_index.py --no-semantic
```

### Keyword + semantic (best results)

```bash
python astronomy_wiki_build_index.py
```

Outputs (default):
- `astronomy_search_store/index/chunks.sqlite3`
- `astronomy_search_store/index/chunks_embeddings.npy` (if semantic built)
- `astronomy_search_store/index/index_meta.json` (if semantic built)

Model cache (for offline use):
- `astronomy_search_store/models/`

## 4) Run the web app and search offline

Start your Flask app as you normally do, then open:
- `/user/wikiqa`

If `chunks_hnsw.bin` exists and the embedding model is cached locally, **semantic search works fully offline**.

