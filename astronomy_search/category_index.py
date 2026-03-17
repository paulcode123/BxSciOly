"""
Build a category tree and page index from the corpus JSONL.
Used for the Browse by Category UI.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from astronomy_search import config


def _display_name(full: str) -> str:
    """Category:Astronomy -> Astronomy"""
    if full.startswith("Category:"):
        return full[9:].strip()
    return full.strip()


def _is_subcategory_of(parent: str, child: str) -> bool:
    """True if child is a logical subcategory of parent (by name prefix)."""
    p_display = _display_name(parent)
    c_display = _display_name(child)
    if not p_display or not c_display:
        return False
    # Child is subcategory if it starts with parent + delimiter
    return c_display.startswith(p_display + " ") or c_display.startswith(p_display + " by ")


def build_category_index(jsonl_path: Path) -> Dict[str, Any]:
    """
    Read corpus JSONL and build:
    - category_to_pages: {full_name: [{title, url, pageid}, ...]}
    - tree: nested {name, display, count, children, pages}
    """
    category_to_pages: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    total_pages = 0

    if not jsonl_path.exists():
        return {"tree": [], "category_to_pages": {}, "total_pages": 0}

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = rec.get("title") or ""
            url = rec.get("url") or ""
            pageid = rec.get("pageid")
            cats = rec.get("categories") or []
            if not isinstance(cats, list):
                continue
            total_pages += 1
            page_entry = {"title": title, "url": url, "pageid": pageid}
            for c in cats:
                c = (c or "").strip()
                if c.startswith("Category:"):
                    category_to_pages[c].append(page_entry)

    # Build tree: find parent for each category (longest prefix match)
    all_cats = sorted(category_to_pages.keys())
    children_of: Dict[str, List[str]] = defaultdict(list)

    for cat in all_cats:
        parent: Optional[str] = None
        parent_len = 0
        for other in all_cats:
            if other == cat:
                continue
            if _is_subcategory_of(other, cat):
                # Prefer longest matching parent
                ol = len(_display_name(other))
                if ol > parent_len:
                    parent = other
                    parent_len = ol
        if parent is not None:
            children_of[parent].append(cat)

    # Recursive tree builder
    def make_node(full_name: str) -> Dict[str, Any]:
        pages = category_to_pages.get(full_name, [])
        child_names = children_of.get(full_name, [])
        children = [make_node(c) for c in sorted(child_names)]
        # Pages belong to this node; child nodes have their own pages
        return {
            "name": full_name,
            "display": _display_name(full_name),
            "count": len(pages),
            "children": children,
            "pages": pages,
        }

    # Roots: categories with no parent in our set
    roots = [c for c in all_cats if not any(_is_subcategory_of(o, c) for o in all_cats if o != c)]
    tree = [make_node(r) for r in sorted(roots, key=lambda x: (-category_to_pages[x].__len__(), x))]

    return {
        "tree": tree,
        "category_to_pages": dict(category_to_pages),
        "total_pages": total_pages,
    }


_cached_index: Optional[Dict[str, Any]] = None
_cached_path: Optional[Path] = None


def get_category_index() -> Dict[str, Any]:
    """Load and cache the category index. Invalidates on file change."""
    global _cached_index, _cached_path
    path = config.pages_jsonl_path()
    if _cached_index is None or _cached_path != path:
        _cached_path = path
        _cached_index = build_category_index(path)
    return _cached_index
