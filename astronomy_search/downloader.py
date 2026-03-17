from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

import requests

from astronomy_search.wiki_api import mw_get


def _normalize_title(title: str) -> str:
    return (title or "").strip().replace("\u200e", "").replace("\u200f", "")


def _is_probably_disambiguation(text: str) -> bool:
    # Cheap heuristic; Wikipedia disambiguation pages are often short and contain "may refer to:".
    t = (text or "").lower()
    return ("may refer to" in t) or ("may stand for" in t)


def _clean_extract(text: str) -> str:
    # MediaWiki extracts are already plaintext when using explaintext=1.
    # We just normalize whitespace a bit.
    text = text or ""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


@dataclass(frozen=True)
class DownloadStats:
    pages_written: int
    bytes_written: int
    categories_seen: int
    pages_seen: int


def iter_category_members(
    category_title: str,
    *,
    session: requests.Session,
    cmtype: str = "page|subcat",
) -> Iterator[Dict[str, object]]:
    """
    Yields categorymembers rows for a category (pages + subcats).
    """
    cmcontinue: Optional[str] = None
    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmtype": cmtype,
            "cmlimit": 500,
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        data = mw_get(params, session=session, min_delay_s=0.15)
        members = (data.get("query") or {}).get("categorymembers") or []
        for m in members:
            yield m

        cont = data.get("continue") or {}
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break


def fetch_page_extracts(
    titles: List[str],
    *,
    session: requests.Session,
) -> List[Dict[str, object]]:
    """
    Fetch plaintext extracts + fullurl for up to ~50 titles at a time.
    """
    if not titles:
        return []

    # MediaWiki API: batch titles with |.
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info|categories",
        "explaintext": 1,
        "redirects": 1,
        "inprop": "url",
        "cllimit": 500,
        "titles": "|".join(titles),
    }
    data = mw_get(params, session=session, min_delay_s=0.1)
    pages = ((data.get("query") or {}).get("pages") or {}).values()

    out: List[Dict[str, object]] = []
    for p in pages:
        if not isinstance(p, dict):
            continue
        if p.get("missing") is not None:
            continue
        pageid = p.get("pageid")
        title = _normalize_title(str(p.get("title") or ""))
        extract = _clean_extract(str(p.get("extract") or ""))
        fullurl = str(p.get("fullurl") or "")
        cats = [
            str(c.get("title") or "").strip()
            for c in (p.get("categories") or [])
            if str(c.get("title") or "").strip().startswith("Category:")
        ]
        rec: Dict[str, object] = {
            "pageid": pageid,
            "title": title,
            "url": fullurl,
            "extract": extract,
        }
        if cats:
            rec["categories"] = cats
        out.append(rec)
    return out


def download_wikipedia_corpus(
    *,
    seed_category: str = "Category:Astronomy",
    out_jsonl: Path,
    max_bytes: int = 1_000_000_000,
    min_chars_per_page: int = 1200,
    max_pages: Optional[int] = None,
    max_categories: int = 50_000,
    status_every: int = 100,
    append: bool = False,
) -> DownloadStats:
    """
    Crawl Wikipedia starting from a seed category and write pages as JSONL.

    Notes:
    - This does NOT download images; it stores plaintext extracts + URL.
    - Size is approximate (bytes written to JSONL).
    """
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    # BFS over categories
    cat_queue: List[str] = [seed_category]
    seen_cats: Set[str] = set()
    seen_pages: Set[int] = set()

    pages_written = 0
    pages_seen = 0
    bytes_written = 0

    # When appending: load existing pageids and file size so we resume correctly
    if append and out_jsonl.exists():
        with out_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line_stripped = line.rstrip("\n")
                if not line_stripped:
                    continue
                try:
                    rec = json.loads(line_stripped)
                    pid = rec.get("pageid")
                    if isinstance(pid, int):
                        seen_pages.add(pid)
                except Exception:
                    pass
        bytes_written = out_jsonl.stat().st_size
        if seen_pages or bytes_written:
            print(f"[resume] existing: {len(seen_pages)} pages, {bytes_written:,} bytes", file=sys.stderr)

    session = requests.Session()
    session.headers.update({"User-Agent": "BxSciOly-AstroWikiQA/1.0 (offline QA indexer)"})

    def should_stop() -> bool:
        if bytes_written >= max_bytes:
            return True
        if max_pages is not None and pages_written >= max_pages:
            return True
        if len(seen_cats) >= max_categories:
            return True
        return False

    mode = "a" if append else "w"
    last_status_at = time.time()
    with out_jsonl.open(mode, encoding="utf-8") as f:
        while cat_queue and not should_stop():
            # Heartbeat so user sees activity even when mostly skipping known pages
            now = time.time()
            if now - last_status_at >= 30:
                print(
                    f"[scan] checked={pages_seen:,} new={pages_written} total={bytes_written:,} bytes "
                    f"cats={len(seen_cats)} queue={len(cat_queue)}",
                    file=sys.stderr,
                )
                last_status_at = now

            cat = cat_queue.pop(0)
            if cat in seen_cats:
                continue
            seen_cats.add(cat)

            # Gather members; batch page title fetches.
            batch_titles: List[str] = []
            for m in iter_category_members(cat, session=session):
                if should_stop():
                    break

                ns = int(m.get("ns") or 0)
                title = _normalize_title(str(m.get("title") or ""))
                if not title:
                    continue

                # ns=14 is Category namespace.
                if ns == 14 and title.startswith("Category:"):
                    if title not in seen_cats:
                        cat_queue.append(title)
                    continue

                # ns=0 is main/article namespace.
                if ns != 0:
                    continue

                # Skip pages we already have (categorymembers returns pageid) - avoids re-fetching
                pid = m.get("pageid")
                if isinstance(pid, int) and pid in seen_pages:
                    continue

                # Accumulate titles to fetch extracts in batches (MediaWiki supports many).
                batch_titles.append(title)
                if len(batch_titles) >= 50:
                    for page in fetch_page_extracts(batch_titles, session=session):
                        if should_stop():
                            break
                        pages_seen += 1
                        pageid = page.get("pageid")
                        if not isinstance(pageid, int):
                            continue
                        if pageid in seen_pages:
                            continue
                        seen_pages.add(pageid)

                        extract = str(page.get("extract") or "")
                        if len(extract) < min_chars_per_page:
                            continue
                        if _is_probably_disambiguation(extract):
                            continue

                        record = {
                            "pageid": pageid,
                            "title": page.get("title"),
                            "url": page.get("url"),
                            "extract": extract,
                            "source": "enwiki",
                            "downloaded_at_unix": int(time.time()),
                        }
                        if page.get("categories"):
                            record["categories"] = page["categories"]
                        line = json.dumps(record, ensure_ascii=False) + "\n"
                        f.write(line)
                        bytes_written += len(line.encode("utf-8"))
                        pages_written += 1

                        if status_every and pages_written % status_every == 0:
                            print(
                                f"[download] pages={pages_written} bytes={bytes_written:,} "
                                f"cats={len(seen_cats)} queue={len(cat_queue)}",
                                file=sys.stderr,
                            )
                    # Heartbeat: print every 30s so user sees activity when mostly skipping
                    now = time.time()
                    if now - last_status_at >= 30:
                        print(
                            f"[scan] checked={pages_seen:,} new={pages_written} total={bytes_written:,} bytes "
                            f"cats={len(seen_cats)} queue={len(cat_queue)}",
                            file=sys.stderr,
                        )
                        last_status_at = now

                    batch_titles = []

            # Flush any remaining titles for this category.
            if batch_titles and not should_stop():
                for page in fetch_page_extracts(batch_titles, session=session):
                    if should_stop():
                        break
                    pages_seen += 1
                    pageid = page.get("pageid")
                    if not isinstance(pageid, int):
                        continue
                    if pageid in seen_pages:
                        continue
                    seen_pages.add(pageid)

                    extract = str(page.get("extract") or "")
                    if len(extract) < min_chars_per_page:
                        continue
                    if _is_probably_disambiguation(extract):
                        continue

                    record = {
                        "pageid": pageid,
                        "title": page.get("title"),
                        "url": page.get("url"),
                        "extract": extract,
                        "source": "enwiki",
                        "downloaded_at_unix": int(time.time()),
                    }
                    if page.get("categories"):
                        record["categories"] = page["categories"]
                    line = json.dumps(record, ensure_ascii=False) + "\n"
                    f.write(line)
                    bytes_written += len(line.encode("utf-8"))
                    pages_written += 1

                    if status_every and pages_written % status_every == 0:
                        print(
                            f"[download] pages={pages_written} bytes={bytes_written:,} "
                            f"cats={len(seen_cats)} queue={len(cat_queue)}",
                            file=sys.stderr,
                        )
                # Heartbeat for remaining batch
                now = time.time()
                if now - last_status_at >= 30:
                    print(
                        f"[scan] checked={pages_seen:,} new={pages_written} total={bytes_written:,} bytes "
                        f"cats={len(seen_cats)} queue={len(cat_queue)}",
                        file=sys.stderr,
                    )
                    last_status_at = now

    return DownloadStats(
        pages_written=pages_written,
        bytes_written=bytes_written,
        categories_seen=len(seen_cats),
        pages_seen=pages_seen,
    )

