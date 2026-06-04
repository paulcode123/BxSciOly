from dotenv import load_dotenv
from pathlib import Path

_ROOT_ENV = Path(__file__).resolve().parent
load_dotenv(_ROOT_ENV / ".env")
load_dotenv(_ROOT_ENV / ".env.local")

import os
from datetime import datetime

from flask import Flask, render_template, url_for, send_from_directory, redirect

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


@app.route("/year-in-pictures")
def year_in_pictures():
    return render_template("year_in_pictures.html")


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
