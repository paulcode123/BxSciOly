"""
generate_gallery_manifest.py

Vercel serves everything inside public/ directly via CDN, completely
separately from your Python code -- which means the website's live code
can never scan that folder itself at runtime. This script does the
scanning locally (on your computer, where the files ARE visible) and
saves the result as a small JSON file that the website reads instead.

RUN THIS ANY TIME YOU ADD, REMOVE, OR REORDER PHOTOS, then commit and
push the updated gallery_manifest.json file along with your photos.

USAGE:
    python generate_gallery_manifest.py

Requires the same packages as app.py (Pillow, pillow-heif) for HEIC
conversion to work the same way it does on your own machine.
"""

import os
import re
import json
from datetime import datetime

try:
    from PIL import Image
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    print("NOTE: pillow-heif not installed locally -- HEIC files will be skipped.")
    print("Run: pip install Pillow pillow-heif\n")

GALLERY_ROOT = os.path.join("public", "static", "gallery")
STATIC_URL_PREFIX = "/static/gallery"


def _humanize(name):
    return name.replace("_", " ").replace("-", " ").strip()


def _displayable_filename(album_path, filename):
    if not filename.lower().endswith((".heic", ".heif")):
        return filename
    if not HEIC_SUPPORT:
        return None

    cache_dir = os.path.join(album_path, "_converted")
    os.makedirs(cache_dir, exist_ok=True)
    converted_name = os.path.splitext(filename)[0] + ".jpg"
    converted_path = os.path.join(cache_dir, converted_name)
    original_path = os.path.join(album_path, filename)

    if not os.path.isfile(converted_path) or os.path.getmtime(original_path) > os.path.getmtime(converted_path):
        try:
            img = Image.open(original_path)
            img.convert("RGB").save(converted_path, "JPEG", quality=88)
        except Exception as e:
            print(f"  Couldn't convert {original_path}: {e}")
            return None

    return f"_converted/{converted_name}"


def build_gallery_albums():
    albums = []
    image_ext = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif")
    video_ext = (".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv")
    valid_ext = image_ext + video_ext

    for category in ("competitions", "events"):
        cat_path = os.path.join(GALLERY_ROOT, category)
        if not os.path.isdir(cat_path):
            continue

        for season in sorted(os.listdir(cat_path), reverse=True):
            season_path = os.path.join(cat_path, season)
            if not os.path.isdir(season_path):
                continue

            def _sort_key(name):
                match = re.match(r"^(\d+)[-_. ]+(.*)$", name)
                if match:
                    return (0, int(match.group(1)), match.group(2))
                return (1, 0, name)

            for album_name in sorted(os.listdir(season_path), key=_sort_key):
                album_path = os.path.join(season_path, album_name)
                if not os.path.isdir(album_path):
                    continue

                media_files = sorted(
                    f for f in os.listdir(album_path)
                    if f.lower().endswith(valid_ext)
                )
                if not media_files:
                    continue

                resolved = []
                for f in media_files:
                    display_path = _displayable_filename(album_path, f)
                    if display_path is None:
                        continue
                    resolved.append({
                        "original": f,
                        "path": display_path,
                        "is_video": f.lower().endswith(video_ext),
                    })
                if not resolved:
                    continue

                cover_candidates = [r for r in resolved if not r["is_video"]]
                cover_item = next(
                    (r for r in resolved if r["original"].lower().startswith("cover") and not r["is_video"]),
                    cover_candidates[0] if cover_candidates else resolved[0],
                )

                date_file = os.path.join(album_path, "date.txt")
                if os.path.isfile(date_file):
                    with open(date_file, "r") as f:
                        date_str = f.read().strip()
                else:
                    mtimes = [os.path.getmtime(os.path.join(album_path, r["original"])) for r in resolved]
                    date_str = datetime.fromtimestamp(min(mtimes)).strftime("%B %Y")

                display_name = re.sub(r"^\d+[-_. ]+", "", album_name)
                rel_base = f"{STATIC_URL_PREFIX}/{category}/{season}/{album_name}"

                albums.append({
                    "season": season,
                    "title": _humanize(display_name),
                    "date": date_str,
                    "category": category,
                    "cover": f"{rel_base}/{cover_item['path']}",
                    "photos": [
                        {
                            "src": f"{rel_base}/{r['path']}",
                            "caption": _humanize(os.path.splitext(r["original"])[0]),
                            "type": "video" if r["is_video"] else "image",
                        }
                        for r in resolved
                    ],
                })
    return albums


def main():
    if not os.path.isdir(GALLERY_ROOT):
        print(f"Couldn't find {GALLERY_ROOT} -- run this from your project's root folder.")
        return

    albums = build_gallery_albums()
    with open("gallery_manifest.json", "w") as f:
        json.dump(albums, f, indent=2)

    print(f"Wrote gallery_manifest.json with {len(albums)} albums:")
    for a in albums:
        print(f"  - {a['season']} / {a['title']} ({len(a['photos'])} items)")
    print("\nNow commit and push gallery_manifest.json along with your photos.")


if __name__ == "__main__":
    main()