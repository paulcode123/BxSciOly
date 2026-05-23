"""Fetch Bronx Science placements from Duosmium for NY regionals and states."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as exc:
        print(f"  fetch failed {url}: {exc}")
        return None


def parse_json_results(data: dict) -> list[tuple[int, str]]:
    """Return list of (place, team_name) from SciolyFF JSON."""
    teams = []
    for rank, entry in enumerate(data.get("teams", []), start=1):
        name = entry.get("name") or entry.get("school") or ""
        if isinstance(name, dict):
            name = name.get("name", str(name))
        # Some formats use explicit rank
        place = entry.get("rank") or entry.get("place") or rank
        teams.append((int(place), str(name)))
    return teams


def find_bronx(teams: list[tuple[int, str]]) -> list[tuple[int, str]]:
    hits = []
    for place, name in teams:
        lower = name.lower()
        if "bronx" in lower and "science" in lower:
            hits.append((place, name))
    return hits


def try_json(slug: str) -> list[tuple[int, str]] | None:
    for suffix in (".json", "/?format=json"):
        url = f"https://www.duosmium.org/results/{slug}{suffix}"
        raw = fetch(url)
        if not raw or raw.strip().startswith("<"):
            continue
        try:
            data = json.loads(raw)
            return parse_json_results(data)
        except json.JSONDecodeError:
            continue
    return None


def parse_html_table(html: str) -> list[tuple[int, str]]:
    """Parse placement from HTML table rows."""
    teams = []
    # Match table rows with rank and team name
    for m in re.finditer(
        r"<tr[^>]*>.*?<td[^>]*>\s*(\d+)\s*</td>.*?<td[^>]*>(.*?)</td>",
        html,
        re.DOTALL | re.IGNORECASE,
    ):
        place = int(m.group(1))
        cell = re.sub(r"<[^>]+>", " ", m.group(2))
        cell = re.sub(r"\s+", " ", cell).strip()
        if cell:
            teams.append((place, cell))
    return teams


def get_placements(slug: str) -> list[tuple[int, str]]:
    teams = try_json(slug)
    if teams:
        return teams
    html = fetch(f"https://www.duosmium.org/results/{slug}/")
    if html:
        return parse_html_table(html)
    return []


# Candidate tournament slugs by season year (2012-2026)
# We'll probe common NY patterns
REGIONAL_PATTERNS = [
    "NY_nyc_north_regional_c",
    "NY_nyc_west_regional_c",
    "NY_nyc_regional_c",
    "NY_manhattan_regional_c",
    "NY_nyc_north_regional_b",
]
STATES_PATTERN = "NY_states_c"

# Known dates from duosmium search / historical records
KNOWN = {
    2026: {"regional": "2026-01-24_NY_nyc_north_regional_c", "states": "2026-03-20_NY_states_c"},
    2025: {"regional": "2025-01-25_NY_nyc_north_regional_c", "states": "2025-03-21_NY_states_c"},
    2024: {"regional": "2024-01-27_NY_nyc_north_regional_c", "states": "2024-03-15_NY_states_c"},
    2023: {"regional": "2023-02-04_NY_nyc_north_regional_c", "states": "2023-03-17_NY_states_c"},
    2022: {"regional": "2022-02-12_NY_nyc_north_regional_c", "states": "2022-03-18_NY_states_c"},
    2021: {"regional": "2021-02-06_NY_nyc_north_regional_c", "states": "2021-03-19_NY_states_c"},
    2020: {"regional": "2020-02-01_NY_nyc_west_regional_c", "states": "2020-03-13_NY_states_c"},
    2019: {"regional": "2019-02-02_NY_nyc_north_regional_c", "states": "2019-03-15_NY_states_c"},
    2018: {"regional": "2018-02-03_NY_nyc_north_regional_c", "states": "2018-03-16_NY_states_c"},
    2017: {"regional": "2017-02-04_NY_nyc_north_regional_c", "states": "2017-03-17_NY_states_c"},
    2016: {"regional": "2016-01-30_NY_nyc_north_regional_c", "states": "2016-03-18_NY_states_c"},
    2015: {"regional": "2015-01-31_NY_nyc_north_regional_c", "states": "2015-04-17_NY_states_b"},
    2014: {"regional": "2014-02-01_NY_nyc_north_regional_c", "states": "2014-03-14_NY_states_c"},
    2013: {"regional": "2013-02-02_NY_nyc_north_regional_c", "states": "2013-04-12_NY_states_c"},
    2012: {"regional": "2012-02-04_NY_nyc_north_regional_c", "states": "2012-03-29_NY_states_c"},
}

results = {}
for year in range(2012, 2027):
    entry = {"year": year}
    for kind in ("regional", "states"):
        slug = KNOWN.get(year, {}).get(kind)
        if not slug:
            entry[kind] = None
            continue
        url = f"https://www.duosmium.org/results/{slug}/"
        teams = get_placements(slug)
        bronx = find_bronx(teams)
        entry[kind] = {
            "url": url,
            "slug": slug,
            "found": bool(teams),
            "bronx": [{"place": p, "team": t} for p, t in bronx],
        }
        if not teams:
            # mark 404
            html = fetch(url)
            entry[kind]["exists"] = html is not None and "404" not in (html or "")[:500]
    results[year] = entry

out = Path(__file__).parent / "duosmium_bxsci_results.json"
out.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"Wrote {out}")
for year, data in results.items():
    reg = data.get("regional") or {}
    st = data.get("states") or {}
    reg_b = reg.get("bronx", []) if reg else []
    st_b = st.get("bronx", []) if st else []
    print(f"{year}: regional={reg_b or 'N/A'} | states={st_b or 'N/A'}")
