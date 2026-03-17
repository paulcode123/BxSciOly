"""
Fetch Wikipedia categories for pages and add them to the corpus JSONL.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Set

import requests

from astronomy_search.wiki_api import mw_get


def fetch_categories_for_pages(
    pageids: List[int],
    *,
    session: requests.Session,
) -> Dict[int, List[str]]:
    """
    Fetch all categories for the given page IDs.
    Returns {pageid: [category_title, ...]}
    """
    if not pageids:
        return {}

    result: Dict[int, List[str]] = {pid: [] for pid in pageids}
    clcontinue: str | None = None

    while True:
        params = {
            "action": "query",
            "format": "json",
            "prop": "categories",
            "pageids": "|".join(str(p) for p in pageids),
            "cllimit": 500,
        }
        if clcontinue:
            params["clcontinue"] = clcontinue

        data = mw_get(params, session=session, min_delay_s=0.1)
        pages = (data.get("query") or {}).get("pages") or {}

        for pid_str, p in pages.items():
            if not isinstance(p, dict):
                continue
            try:
                pid = int(pid_str)
            except ValueError:
                continue
            cats = p.get("categories") or []
            for c in cats:
                title = (c.get("title") or "").strip()
                if title.startswith("Category:"):
                    result.setdefault(pid, []).append(title)

        cont = data.get("continue") or {}
        clcontinue = cont.get("clcontinue")
        if not clcontinue:
            break

    return result
