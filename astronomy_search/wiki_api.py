from __future__ import annotations

import time
from typing import Any, Dict, Optional

import requests


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"


class MediaWikiError(RuntimeError):
    pass


def mw_get(
    params: Dict[str, Any],
    *,
    session: Optional[requests.Session] = None,
    timeout_s: int = 30,
    max_retries: int = 5,
    min_delay_s: float = 0.1,
) -> Dict[str, Any]:
    """
    Call the MediaWiki API with retries and a small politeness delay.
    Returns parsed JSON dict or raises MediaWikiError.
    """
    s = session or requests.Session()
    last_err: Optional[Exception] = None

    # Politeness delay between calls (especially important when crawling categories).
    if min_delay_s:
        time.sleep(min_delay_s)

    for attempt in range(max_retries):
        try:
            resp = s.get(WIKIPEDIA_API, params=params, timeout=timeout_s)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise MediaWikiError(str(data["error"]))
            return data
        except Exception as e:
            last_err = e
            # Exponential-ish backoff.
            time.sleep(min(10.0, (2 ** attempt) * 0.5))

    raise MediaWikiError(f"MediaWiki API failed after retries: {last_err}")

