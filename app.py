from dotenv import load_dotenv
from pathlib import Path
_ROOT_ENV = Path(__file__).resolve().parent
load_dotenv(_ROOT_ENV / ".env")
load_dotenv(_ROOT_ENV / ".env.local")
import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, url_for, send_from_directory, redirect

# --- Optional HEIC support --------------------------------------------------
# Browsers can't display .heic/.heif files directly (it's an Apple-only
# format), so we convert them to .jpg the first time they're seen and cache
# the result. If the required packages aren't installed, HEIC files are
# just skipped -- everything else on the site keeps working normally.
try:
    from PIL import Image
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
# ---------------------------------------------------------------------------
from articles import ARTICLES
from routes.api_routes import api_routes
from routes.firebase_routes import firebase_routes
from routes.stub_routes import stub_routes
_ROOT = os.path.dirname(os.path.abspath(__file__))
_PUBLIC_STATIC = os.path.join(_ROOT, "public", "static")
app = Flask(
    __name__,
    static_folder=_PUBLIC_STATIC if os.path.isdir(_PUBLIC_STATIC) else "static",
    static_url_path="/static",
)
app.register_blueprint(api_routes)
app.register_blueprint(firebase_routes)
app.register_blueprint(stub_routes)
app.config["SECRET_KEY"] = (
    os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY") or "dev-secret-change-me"
)
MEMBER_PORTAL_PATHS = (
    "/user/meetings",
    "/user/competitions",
    "/user/application",
    "/user/competition/apply",
    "/admin/dashboard",
    "/admin/attendance",
    "/admin/members",
    "/admin/event-placements",
)
# --- Gallery auto-upload system -------------------------------------------
# Scans static/gallery/competitions/<season>/<album>/*.jpg and
# static/gallery/events/<season>/<album>/*.jpg and builds the album list
# the gallery page needs. Drop a new photo or folder in and it shows up
# automatically -- no code changes needed.
GALLERY_ROOT = os.path.join(app.static_folder, "gallery")


def _humanize(name):
    """Turn a folder/file name into a readable label."""
    return name.replace("_", " ").replace("-", " ").strip()


def _displayable_filename(album_path, filename):
    """
    If filename is a HEIC/HEIF file, convert it to a cached .jpg (once) and
    return that filename instead. Otherwise return filename unchanged.
    Returns None if it's HEIC but conversion isn't available/possible, so
    the caller can skip it rather than link to something browsers can't show.
    """
    if not filename.lower().endswith((".heic", ".heif")):
        return filename

    if not HEIC_SUPPORT:
        return None

    cache_dir = os.path.join(album_path, "_converted")
    os.makedirs(cache_dir, exist_ok=True)
    converted_name = os.path.splitext(filename)[0] + ".jpg"
    converted_path = os.path.join(cache_dir, converted_name)
    original_path = os.path.join(album_path, filename)

    # Only (re)convert if we don't already have an up-to-date cached copy.
    if not os.path.isfile(converted_path) or os.path.getmtime(original_path) > os.path.getmtime(converted_path):
        try:
            img = Image.open(original_path)
            img.convert("RGB").save(converted_path, "JPEG", quality=88)
        except Exception:
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

            # Sort album folders using an optional leading number prefix
            # (e.g. "1-Regionals", "2-States") so you control the order.
            # Folders without a prefix just fall back to alphabetical order.
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

                # Resolve each file to what should actually be linked to.
                # For normal images/videos this is just the filename itself.
                # For HEIC/HEIF, this converts (and caches) a .jpg version,
                # since browsers can't display HEIC directly. Anything that
                # can't be converted (or where conversion isn't installed)
                # is skipped rather than linked to a broken file.
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

                # Prefer a file named "cover", but a cover should always be
                # an image (not a video) so it displays as a thumbnail.
                cover_candidates = [r for r in resolved if not r["is_video"]]
                cover_item = next(
                    (r for r in resolved if r["original"].lower().startswith("cover") and not r["is_video"]),
                    cover_candidates[0] if cover_candidates else resolved[0],
                )

                # Date: prefer an optional date.txt file inside the album
                # folder (e.g. containing "January 2026") since file
                # modification times aren't reliable once photos have been
                # copied, zipped, or re-uploaded. Falls back to file dates
                # only if no date.txt is present.
                date_file = os.path.join(album_path, "date.txt")
                if os.path.isfile(date_file):
                    with open(date_file, "r") as f:
                        date_str = f.read().strip()
                else:
                    mtimes = [os.path.getmtime(os.path.join(album_path, r["original"])) for r in resolved]
                    date_str = datetime.fromtimestamp(min(mtimes)).strftime("%B %Y")

                # Strip any ordering prefix (e.g. "1-") before turning the
                # folder name into a display title.
                display_name = re.sub(r"^\d+[-_. ]+", "", album_name)
                rel_base = f"gallery/{category}/{season}/{album_name}"

                albums.append({
                    "season": season,
                    "title": _humanize(display_name),
                    "date": date_str,
                    "category": category,
                    "cover": url_for("static", filename=f"{rel_base}/{cover_item['path']}"),
                    "photos": [
                        {
                            "src": url_for("static", filename=f"{rel_base}/{r['path']}"),
                            "caption": _humanize(os.path.splitext(r["original"])[0]),
                            "type": "video" if r["is_video"] else "image",
                        }
                        for r in resolved
                    ],
                })
    return albums
# ---------------------------------------------------------------------------
@app.route("/debug/gallery-check")
def debug_gallery_check():
    info = {
        "GALLERY_ROOT": GALLERY_ROOT,
        "gallery_root_exists": os.path.isdir(GALLERY_ROOT),
        "static_folder": app.static_folder,
        "static_folder_exists": os.path.isdir(app.static_folder),
        "static_folder_contents": os.listdir(app.static_folder) if os.path.isdir(app.static_folder) else "NOT FOUND",
        "heic_support": HEIC_SUPPORT,
    }
    return json.dumps(info, indent=2)

@app.context_processor
def inject_now():
    return {
        "now": datetime.now(),
        "vercel_analytics": bool(os.environ.get("VERCEL")),
        "member_portal_paths": list(MEMBER_PORTAL_PATHS),
    }
@app.template_filter("datetime")
def format_datetime(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d")
# --- Public pages ---
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/leadership")
def leadership():
    return render_template("leadership.html")
@app.route("/our-team")
def our_team():
    return render_template("our_team.html")
@app.route("/what-we-do")
def what_we_do():
    return render_template("what_we_do.html")
@app.route("/register")
def register():
    return render_template("register.html")
@app.route("/post-registration")
def post_registration():
    return render_template("post_registration.html")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/reset-password")
def reset_password_page():
    return render_template("reset_password.html")
@app.route("/calendar")
def calendar():
    return render_template("calendar.html")
@app.route("/articles")
def articles():
    return render_template("articles.html", articles=ARTICLES)
@app.route("/articles/ultimate-guide")
def article_ultimate_guide():
    return render_template("articles/ultimate_guide.html")

@app.route("/faq")
def faq():
    return redirect(url_for("articles"), code=301)

@app.route("/events/biology")
def events_biology():
    return render_template("events/biology.html")
@app.route("/events/chemistry")
def events_chemistry():
    return render_template("events/chemistry.html")
@app.route("/events/inquiry")
def events_inquiry():
    return render_template("events/inquiry.html")
@app.route("/events/earth-science-classification")
def earth_science_classification():
    return render_template("events/earth_science_classification.html")
@app.route("/events/physics-design")
def physics_design():
    return render_template("events/physics_design.html")
@app.route("/events/construction-build")
def construction_build():
    return redirect(url_for("home"), code=301)
@app.route("/events/precision-build")
def precision_build():
    return redirect(url_for("home"), code=301)
@app.route("/events/earth-science")
def events_earth_science():
    return redirect(url_for("earth_science_classification"), code=301)
@app.route("/events/classification-compilation")
def classification_compilation():
    return redirect(url_for("earth_science_classification"), code=301)
@app.route("/events/chemistry-inquiry")
def chemistry_inquiry():
    return redirect(url_for("events_chemistry"), code=301)
@app.route("/sponsors")
def sponsors():
    return render_template("sponsors.html")
@app.route("/gallery")
def gallery():
    albums = build_gallery_albums()
    return render_template("gallery.html", albums_json=json.dumps(albums))
@app.route("/Merch")
def merch():
    return render_template("merch.html")
# --- Simulators (public) ---
@app.route("/user/bungee-calculator")
def bungee_calculator():
    return render_template("bungee_drop_calculator.html")
@app.route("/user/ev-simulator")
def ev_simulator():
    return render_template("ev_simulator.html")
@app.route("/user/robot-tour-simulator")
def robot_tour_simulator():
    return render_template("robot_tour_simulator.html")
# --- Member portal ---
@app.route("/user/meetings")
def user_meetings():
    return render_template("user/meetings.html")
@app.route("/user/competitions")
def user_competitions():
    return render_template("user/competitions.html", now=datetime.now())
@app.route("/user/application")
def user_application():
    return render_template("user/application.html")
@app.route("/user/competition/apply")
def competition_apply():
    return render_template("user/competition_apply.html")
@app.route("/user/settings")
def user_settings():
    return render_template("user/settings.html")
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")
@app.route("/admin/attendance")
def admin_attendance():
    return render_template("admin_attendance.html")
@app.route("/admin/members")
def admin_members():
    return render_template("admin_members.html")
@app.route("/admin/event-placements")
def admin_event_placements():
    return render_template("admin_event_placements.html")
@app.route("/user/learning")
@app.route("/user/events")
@app.route("/user/events/binder")
@app.route("/user/conversations")
@app.route("/user/learning/topicspace")
def removed_member_pages():
    return redirect(url_for("home"), code=302)
@app.route("/templates/approved_emails.txt")
def serve_approved_emails():
    return send_from_directory("templates", "approved_emails.txt")
if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)