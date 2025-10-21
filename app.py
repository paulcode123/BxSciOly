from flask import Flask, render_template, url_for, send_from_directory, request, jsonify, make_response
from datetime import datetime, timedelta
import os
import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import csv
from routes.firebase_routes import firebase_routes
try:
    # Prefer shared initialization
    from db_init import db as firebase_db
except Exception:
    # Fallback to the db client initialized in firebase routes
    from routes.firebase_routes import db as firebase_db
from firebase_admin import firestore
from routes.test_parsing_routes import test_parsing_routes

app = Flask(__name__)
app.register_blueprint(firebase_routes)
app.register_blueprint(test_parsing_routes)

# Secret key configuration for signing tokens/cookies
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'dev-secret-change-me'

def _get_serializer(salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt=salt)

INTEREST_TOKEN_SALT = 'interest-meeting-token'
INTEREST_VERIFY_SALT = 'interest-meeting-verified'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.template_filter('datetime')
def format_datetime(date_string):
    """
    Convert a date string to a datetime object for comparison
    """
    return datetime.strptime(date_string, '%Y-%m-%d')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/leadership')
def leadership():
    return render_template('leadership.html')

@app.route('/our-team')
def our_team():
    return render_template('our_team.html')

@app.route('/what-we-do')
def what_we_do():
    return render_template('what_we_do.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/post-registration')
def post_registration():
    return render_template('post_registration.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/reset-password')
def reset_password_page():
    return render_template('reset_password.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')



@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/bug-submission')
def bug_submission():
    return render_template('bug_submission.html')

@app.route('/strategic-plan')
def strategic_plan():
    return render_template('strategic_plan.html')

@app.route('/house-cup')
def house_cup():
    return render_template('house_cup.html')

@app.route('/HouseCupTheme')
def house_cup_theme():
    return render_template('house_cup_theme.html')

@app.route('/summer-learning-project')
def summer_learning_project():
    return render_template('summer_learning_project.html')

# New subject-based event routes
@app.route('/events/construction-build')
def construction_build():
    return render_template('events/construction_build.html')

@app.route('/events/precision-build')
def precision_build():
    return render_template('events/precision_build.html')

@app.route('/events/physics-design')
def physics_design():
    return render_template('events/physics_design.html')

@app.route('/events/earth-science')
def events_earth_science():
    return render_template('events/earth_science.html')

@app.route('/events/classification-compilation')
def classification_compilation():
    return render_template('events/classification_compilation.html')

@app.route('/events/biology')
def events_biology():
    return render_template('events/biology.html')

@app.route('/events/chemistry-inquiry')
def chemistry_inquiry():
    return render_template('events/chemistry_inquiry.html')

@app.route('/firebase-demo')
def firebase_demo():
    return render_template('firebase_demo.html')

# User account routes
@app.route('/user/events')
def user_events():
    return render_template('user/events.html')

@app.route('/user/events/path')
def user_events_learning_path():
    return render_template('user/learning_path.html')

@app.route('/user/events/binder')
def user_events_binder_editor():
    return render_template('user/binder_editor.html')

@app.route('/user/events/test')
def user_events_test_viewer():
    return render_template('user/test_viewer.html')

@app.route('/events/academic')
def academic_events():
    return render_template('events/academic_events.html')

@app.route('/events/build')
def build_events():
    return render_template('events/build_events.html')

@app.route('/user/binders')
def user_binders():
    return render_template('user/binders.html')

@app.route('/user/binder/<binder_id>')
def user_binder_editor(binder_id):
    return render_template('user/binder_editor.html', binder_id=binder_id)

@app.route('/user/competitions')
def user_competitions():
    # For testing: Let's make "now" be between specific dates for demonstrating button visibility
    # In a real app, you'd use the actual datetime.now() instead
    test_date = datetime.strptime('2025-09-25', '%Y-%m-%d')
    return render_template('user/competitions.html', now=test_date)

@app.route('/user/settings')
def user_settings():
    return render_template('user/settings.html')

# Public event detail pages (not in nav)
@app.route('/event/<event_slug>')
def event_detail(event_slug):
    # Render a general-purpose event detail template; client JS will fetch content
    return render_template('event_detail.html', event_slug=event_slug)

@app.route('/user/conversations')
def user_conversations():
    # Backward-compatible route now points to the new Learning page
    return render_template('user/learning.html')

@app.route('/user/competition/apply')
def competition_apply():
    return render_template('user/competition_apply.html')

@app.route('/user/topic-space')
def topic_space():
    return render_template('user/topic_space.html')

@app.route('/user/topic-space/<parsed_test_id>')
def topic_space_visualization(parsed_test_id):
    return render_template('user/topic_space.html', parsed_test_id=parsed_test_id)

@app.route('/user/parsed-test/<parsed_test_id>')
def parsed_test_view(parsed_test_id):
    return render_template('user/parsed_test.html', parsed_test_id=parsed_test_id)

@app.route('/user/attendance')
def user_attendance():
    return render_template('user/attendance.html')

@app.route('/user/meetings')
def user_meetings():
    return render_template('user/meetings.html')

@app.route('/user/admin/attendance')
def user_admin_attendance():
    return render_template('user/admin_attendance.html')

@app.route('/user/learning')
def user_learning():
    return render_template('user/learning.html')

@app.route('/user/application')
def user_application():
    return render_template('user/application.html')

@app.route('/DiagResults')
def diag_results():
    return render_template('user/diag_results.html')

@app.route('/api/roster-status/<user_id>')
def api_roster_status(user_id):
    """Check if a user is on the team roster"""
    try:
        # Read team_placement_solution.csv to check if user is on roster
        with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['firebaseID'] == user_id:
                    return jsonify({'onRoster': True}), 200
        
        return jsonify({'onRoster': False}), 200
    except Exception as e:
        print(f"Error checking roster status: {e}")
        return jsonify({'error': 'Internal server error', 'onRoster': False}), 500

@app.route('/api/diag-results/<user_id>')
def api_diag_results(user_id):
    """Fetch diagnostic results for a specific user by Firebase UID"""
    try:
        # First, get the bxsciolyID from the member mapping CSV
        bxscioly_id = None
        with open('Planning/SCIOLY MEMBER IDS - member_names_ids_20250929_074942.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == user_id:
                    # Extract just the number part (e.g., "bxscioly_99673" -> "99673")
                    bxscioly_full = row['bxscioly_number']
                    if bxscioly_full and bxscioly_full.startswith('bxscioly_'):
                        bxscioly_id = bxscioly_full.replace('bxscioly_', '')
                    break
        
        if not bxscioly_id:
            return jsonify({'error': 'User not found in member mapping'}), 404
        
        # Read consolidated_scores.csv using the extracted bxsciolyID
        consolidated_data = {}
        with open('Planning/consolidated_scores.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['bxsciolyID'] == bxscioly_id:
                    consolidated_data = row
                    break
        
        if not consolidated_data:
            return jsonify({'error': 'No diagnostic results found for this user'}), 404
        
        # Parse events taken
        events_taken = []
        for i in range(1, 9):
            event_key = f'Event{i}'
            score_key = f'Score{i}'
            if event_key in consolidated_data and consolidated_data[event_key]:
                event_name = consolidated_data[event_key]
                score = consolidated_data[score_key]
                events_taken.append({
                    'name': event_name,
                    'score': float(score) if score else 0
                })
        
        # Check if user made the team
        made_team = False
        team_data = {}
        with open('Planning/team_placement_solution.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['bxsciolyID'] == bxscioly_id:
                    made_team = True
                    team_data = row
                    break
        
        # Get event-specific rankings and percentiles
        event_details = {}
        with open('Planning/team_placement_by_event.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['bxsciolyID'] == bxscioly_id:
                    event_name = row['event']
                    event_details[event_name] = {
                        'rank': int(row['eventRank']),
                        'percentile': float(row['eventPercentile']),
                        'position': int(row['position']) if made_team else None
                    }
        
        # Calculate rankings and percentiles for ALL events from consolidated_scores.csv
        # This gives feedback even for events the user wasn't assigned to
        event_scores = {}  # {event_name: [(score, bxsciolyID), ...]}
        with open('Planning/consolidated_scores.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for i in range(1, 9):
                    event_key = f'Event{i}'
                    score_key = f'Score{i}'
                    if event_key in row and row[event_key] and score_key in row and row[score_key]:
                        event_name = row[event_key]
                        score = float(row[score_key])
                        if event_name not in event_scores:
                            event_scores[event_name] = []
                        event_scores[event_name].append((score, row['bxsciolyID']))
        
        # Calculate total participants per event and rank/percentile for this user
        event_totals = {}
        for event_name, scores in event_scores.items():
            event_totals[event_name] = len(scores)
            
            # If this user took this event, calculate their rank and percentile
            user_score = None
            for score, bid in scores:
                if bid == bxscioly_id:
                    user_score = score
                    break
            
            # If this user took this event but it's not in event_details yet, calculate from scores
            if user_score is not None and event_name not in event_details:
                # Sort scores in descending order (higher is better)
                sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
                rank = next(i for i, (s, bid) in enumerate(sorted_scores) if bid == bxscioly_id) + 1
                percentile = ((len(sorted_scores) - rank + 1) / len(sorted_scores)) * 100
                
                event_details[event_name] = {
                    'rank': rank,
                    'percentile': percentile,
                    'position': None  # Not assigned to this event
                }
        
        result = {
            'firstName': consolidated_data['firstName'],
            'lastName': consolidated_data['lastName'],
            'avgPercentile': float(consolidated_data['avgPercentile']) if consolidated_data['avgPercentile'] else 0,
            'eventsTaken': events_taken,
            'madeTeam': made_team,
            'eventDetails': event_details,
            'eventTotals': event_totals
        }
        
        if made_team:
            # Parse assigned events
            assigned_events = []
            for i in range(1, 4):
                event_key = f'event{i}'
                if event_key in team_data and team_data[event_key]:
                    assigned_events.append(team_data[event_key])
            
            result['assignedEvents'] = assigned_events
            result['house'] = team_data['house']
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error fetching diag results: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/attendance')
def admin_attendance():
    return render_template('admin_attendance.html')

@app.route('/admin/events')
def admin_events():
    return render_template('admin_events.html')

@app.route('/admin/content')
def admin_content():
    return render_template('admin_content.html')

@app.route('/admin/calendar')
def admin_calendar():
    return render_template('admin_calendar.html')

@app.route('/admin/members')
def admin_members():
    return render_template('admin_members.html')

@app.route('/admin/analytics')
def admin_analytics():
    return render_template('admin_analytics.html')

@app.route('/admin/learning-conversations')
def admin_learning_conversations():
    return render_template('admin_learning_conversations.html')

@app.route('/admin/competitions')
def admin_competitions():
    return render_template('admin_competitions.html')

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/sponsors')
def sponsors():
    return render_template('sponsors.html')

@app.route('/templates/approved_emails.txt')
def serve_approved_emails():
    return send_from_directory('templates', 'approved_emails.txt')

# ----------------------- Interest Meeting Attendance -----------------------

@app.route('/admin/interestCode')
def admin_interest_code():
    return render_template('admin_interest_code.html')


@app.route('/api/interest/token')
def api_interest_token():
    # Admin guard similar to other admin APIs: require an admin header token/id
    admin_id = request.headers.get('X-Admin-ID')
    if not admin_id:
        return jsonify({'error': 'unauthorized'}), 401
    # Generate a short-lived signed token; valid for 20 seconds upon verification
    payload = {
        'nonce': secrets.token_urlsafe(8),
        'issued_at': datetime.utcnow().isoformat()
    }
    token = _get_serializer(INTEREST_TOKEN_SALT).dumps(payload)
    full_url = url_for('interest_meeting', token=token, _external=True)
    return jsonify({'token': token, 'url': full_url})


@app.route('/interestMeeting')
def interest_meeting():
    # Renders the attendee page; client JS will verify token and then clean URL
    return render_template('interest_meeting.html')


@app.route('/api/interest/verify', methods=['POST'])
def api_interest_verify():
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    if not token:
        return jsonify({'ok': False, 'error': 'missing_token'}), 400
    try:
        _get_serializer(INTEREST_TOKEN_SALT).loads(token, max_age=20)
    except SignatureExpired:
        return jsonify({'ok': False, 'error': 'expired'}), 400
    except BadSignature:
        return jsonify({'ok': False, 'error': 'invalid'}), 400

    # Issue a short-lived verification cookie (e.g., 5 minutes) so users can submit after form entry
    verified_value = _get_serializer(INTEREST_VERIFY_SALT).dumps({'v': True})
    resp = make_response(jsonify({'ok': True}))
    # 5 minutes validity
    resp.set_cookie('interest_verified', verified_value, max_age=300, httponly=True, samesite='Lax')
    return resp


@app.route('/api/interest/submit', methods=['POST'])
def api_interest_submit():
    # Prevent duplicates via cookie
    if request.cookies.get('interest_submitted') == '1':
        return jsonify({'ok': False, 'error': 'already_submitted'}), 409

    # Require a recent verification cookie
    verified_cookie = request.cookies.get('interest_verified')
    if not verified_cookie:
        return jsonify({'ok': False, 'error': 'not_verified'}), 403
    try:
        _get_serializer(INTEREST_VERIFY_SALT).loads(verified_cookie, max_age=300)
    except Exception:
        return jsonify({'ok': False, 'error': 'verify_expired'}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    grade = (data.get('grade') or '').strip()
    email = (data.get('email') or '').strip()

    if not name or not grade or not email:
        return jsonify({'ok': False, 'error': 'missing_fields'}), 400

    # Append to CSV file
    record_time = datetime.utcnow().isoformat()
    user_agent = request.headers.get('User-Agent', '')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    csv_path = 'interest_meeting_attendance.csv'
    try:
        need_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(['timestamp', 'name', 'grade', 'email', 'ip', 'user_agent'])
            writer.writerow([record_time, name, grade, email, ip, user_agent])
    except Exception as e:
        return jsonify({'ok': False, 'error': 'write_failed'}), 500

    # Firestore write to interestAttendance collection
    try:
        firebase_db.collection('interestAttendance').add({
            'name': name,
            'grade': grade,
            'email': email,
            'ip': ip,
            'userAgent': user_agent,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    except Exception:
        # Do not fail the whole submission if Firestore write fails; CSV already recorded
        pass

    resp = make_response(jsonify({'ok': True}))
    # Prevent duplicates for this device/browser
    resp.set_cookie('interest_submitted', '1', max_age=60*60*24*180, httponly=True, samesite='Lax')
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000) 