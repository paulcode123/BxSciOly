"""
Backfill categories for all pages in the astronomy Wikipedia corpus.
Reads the JSONL, fetches each page's categories from the Wikipedia API,
and writes an updated JSONL with a "categories" field on each record.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

from astronomy_search import config
from astronomy_search.fetch_categories import fetch_categories_for_pages


def main() -> None:
    p = argparse.ArgumentParser(description="Add Wikipedia categories to corpus JSONL")
    p.add_argument("--in", dest="input_", default=str(config.pages_jsonl_path()), help="Input JSONL path")
    p.add_argument("--out", default=None, help="Output JSONL path (default: overwrite input)")
    p.add_argument("--batch", type=int, default=50, help="Page IDs per API batch")
    p.add_argument("--status", type=int, default=100, help="Print progress every N pages")
    args = p.parse_args()

    in_path = Path(args.input_)
    out_path = Path(args.out) if args.out else in_path
    if not in_path.exists():
        print(f"[error] Input not found: {in_path}", file=sys.stderr)
        raise SystemExit(2)

    # Load all records
    records: list[dict] = []
    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError:
                continue

    n = len(records)
    print(f"[backfill] {n:,} pages to process", file=sys.stderr)

    session = requests.Session()
    session.headers["User-Agent"] = "BxSciOly-AstroWikiQA/1.0 (category backfill)"

    # Fetch categories in batches
    pageid_to_idx: dict[int, int] = {}
    for i, rec in enumerate(records):
        pid = rec.get("pageid")
        if isinstance(pid, int):
            pageid_to_idx[pid] = i

    batch_size = args.batch
    processed = 0
    for start in range(0, n, batch_size):
        batch = records[start : start + batch_size]
        pageids = [r["pageid"] for r in batch if isinstance(r.get("pageid"), int)]
        if not pageids:
            continue

        try:
            cat_map = fetch_categories_for_pages(pageids, session=session)
        except Exception as e:
            print(f"[error] batch at {start}: {e}", file=sys.stderr)
            continue

        for pid, cats in cat_map.items():
            idx = pageid_to_idx.get(pid)
            if idx is not None:
                records[idx]["categories"] = cats

        processed += len(pageids)
        if args.status and processed % args.status == 0:
            print(f"[backfill] {processed:,}/{n:,} pages", file=sys.stderr)

    # Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    tmp_path.replace(out_path)
    print(f"[backfill] Done. Wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
