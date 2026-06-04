"""Placeholder API responses for features not yet migrated off Firebase."""

from flask import Blueprint, jsonify

stub_routes = Blueprint("stub_routes", __name__)

_MSG = "This feature is temporarily unavailable."


def _unavailable():
    return jsonify({"error": _MSG}), 503


@stub_routes.route("/api/bungee/export", methods=["POST"])
@stub_routes.route("/api/bungee/data", methods=["GET", "POST"])
@stub_routes.route("/api/robot-tour/tracks", methods=["GET", "POST"])
@stub_routes.route("/api/CalendarEvents", methods=["GET"])
@stub_routes.route("/api/Competitions", methods=["GET"])
@stub_routes.route("/api/Applications", methods=["GET", "POST"])
@stub_routes.route("/api/Applications/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/Events", methods=["GET"])
@stub_routes.route("/api/Events/<path:rest>", methods=["GET", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/Meeting", methods=["GET", "POST"])
@stub_routes.route("/api/Meeting/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/Members", methods=["GET"])
@stub_routes.route("/api/Binders", methods=["GET", "POST"])
@stub_routes.route("/api/Binders/<path:rest>", methods=["GET", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/Tests", methods=["GET", "POST"])
@stub_routes.route("/api/Tests/<path:rest>", methods=["GET", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/ExcusedAbsences", methods=["GET", "POST"])
@stub_routes.route("/api/ExcusedAbsences/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/HouseCupPoints", methods=["GET", "POST"])
@stub_routes.route("/api/HouseCupPoints/<path:rest>", methods=["GET", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/LearningResources/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/LearningModules/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/LearningConversations/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/ModuleCompletions/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@stub_routes.route("/api/profile-photo", methods=["POST"])
@stub_routes.route("/api/admin/<path:rest>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def api_unavailable(**kwargs):
    return _unavailable()
