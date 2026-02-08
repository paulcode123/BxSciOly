from __future__ import annotations

import argparse
from pathlib import Path

from astronomy_search import config
from astronomy_search.downloader import download_wikipedia_corpus


def main() -> None:
    p = argparse.ArgumentParser(description="Download ~1GB of astronomy Wikipedia plaintext for offline QA.")
    p.add_argument("--seed-category", default="Category:Astronomy", help="Wikipedia category title to crawl from")
    p.add_argument("--max-bytes", type=int, default=1_000_000_000, help="Approx bytes to write to JSONL")
    p.add_argument("--min-chars", type=int, default=1200, help="Skip pages with shorter extracts")
    p.add_argument("--max-pages", type=int, default=None, help="Optional cap on pages written")
    p.add_argument("--out", default=str(config.pages_jsonl_path()), help="Output JSONL path")
    p.add_argument("--append", action="store_true", help="Append to existing JSONL instead of overwriting")
    args = p.parse_args()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = config.repo_root() / out_path

    stats = download_wikipedia_corpus(
        seed_category=args.seed_category,
        out_jsonl=out_path,
        max_bytes=args.max_bytes,
        min_chars_per_page=args.min_chars,
        max_pages=args.max_pages,
        append=bool(args.append),
    )
    print(stats)


if __name__ == "__main__":
    main()

