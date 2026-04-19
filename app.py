from flask import Flask, render_template, url_for, send_from_directory, request, jsonify, make_response, redirect
from urllib.parse import quote
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
try:
    from routes.wikiqa_routes import wikiqa_routes
    WIKIQA_AVAILABLE = True
except ImportError:
    WIKIQA_AVAILABLE = False
    wikiqa_routes = None

app = Flask(__name__)
app.register_blueprint(firebase_routes)
app.register_blueprint(test_parsing_routes)
if WIKIQA_AVAILABLE:
    app.register_blueprint(wikiqa_routes)

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

@app.route('/Merch')
def merch():
    return render_template('merch.html')

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

@app.route('/user/learning/topicspace')
def user_learning_topicspace():
    return render_template('user/learning_topicspace.html')

@app.route('/user/application')
def user_application():
    return render_template('user/application.html')

@app.route('/DiagResults')
def diag_results():
    return render_template('user/diag_results.html')

@app.route('/user/bungee-calculator')
def bungee_calculator():
    return render_template('bungee_drop_calculator.html')

@app.route('/user/ev-simulator')
def ev_simulator():
    return render_template('ev_simulator.html')

@app.route('/user/robot-tour-simulator')
def robot_tour_simulator():
    return render_template('robot_tour_simulator.html')

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

import bungee_utils

# ----------------------- Bungee Calculator -----------------------
# Single shared document for team-wide bungee data

BUNGEE_DOC_ID = 'shared'  # Single document ID for all team data
@app.route('/api/bungee/export', methods=['POST'])
def export_bungee_model():
    """Calculate the full bungee model based on calibration and damping"""
    try:
        data = request.get_json()
        calibration_data = data.get('calibrationData', [])
        method = data.get('interpolationMethod', 'linear')
        gamma = float(data.get('gamma', 0.95))
        bottle_height = float(data.get('bottleHeight', 30.0))
        target_dist = float(data.get('targetDistance', 2.0))
        area_m2 = float(data.get('bottleArea', 0.0045))
        cd = float(data.get('dragCoefficient', 1.0))
        
        if not calibration_data:
            return jsonify({'error': 'No calibration data provided'}), 400

        # Validate calibration data format (expects strain, force keys)
        valid_data = []
        for p in calibration_data:
            if isinstance(p, dict) and 'strain' in p and 'force' in p:
                valid_data.append({
                    'strain': float(p['strain']),
                    'force': float(p['force'])
                })
        if not valid_data:
            return jsonify({'error': 'Calibration data must have strain and force values'}), 400
            
        result = bungee_utils.generate_bungee_export(
            valid_data, method, gamma, bottle_height, target_dist, area_m2, cd
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"Error generating bungee export: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bungee/data', methods=['GET'])
def get_bungee_data():
    """Fetch the shared bungee data document"""
    try:
        doc_ref = firebase_db.collection('BungeeStrings').document(BUNGEE_DOC_ID)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return jsonify(data), 200
        else:
            # Return empty structure if document doesn't exist
            return jsonify({
                'id': BUNGEE_DOC_ID,
                'strings': [],
                'notes': '',
                'interpolationMethod': 'linear'
            }), 200
    except Exception as e:
        print(f"Error fetching bungee data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bungee/data', methods=['POST'])
def save_bungee_data():
    """Save the shared bungee data document"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Ensure we always update the same document
        data['updatedAt'] = firestore.SERVER_TIMESTAMP
        
        doc_ref = firebase_db.collection('BungeeStrings').document(BUNGEE_DOC_ID)
        doc = doc_ref.get()
        
        if doc.exists:
            # Update existing
            doc_ref.update(data)
        else:
            # Create new with timestamp
            data['createdAt'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(data)
        
        return jsonify({'id': BUNGEE_DOC_ID, 'message': 'Data saved successfully'}), 200
            
    except Exception as e:
        print(f"Error saving bungee data: {e}")
        return jsonify({'error': str(e)}), 500

# ----------------------- Robot Tour Simulator -----------------------
ROBOT_TOUR_DOC_ID = 'shared'

def _serialize_robot_tour_track(t):
    """Make track JSON-serializable (Firestore Timestamp -> ISO string)"""
    t = dict(t)
    ca = t.get('createdAt')
    if ca and not isinstance(ca, str):
        try:
            if hasattr(ca, 'isoformat'):
                t['createdAt'] = ca.isoformat()
        except Exception:
            t['createdAt'] = str(ca)
    return t

@app.route('/api/robot-tour/tracks', methods=['GET'])
def get_robot_tour_tracks():
    """Fetch the shared Robot Tour track configs"""
    try:
        doc_ref = firebase_db.collection('RobotTourTracks').document(ROBOT_TOUR_DOC_ID)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            tracks = [_serialize_robot_tour_track(t) for t in data.get('tracks', [])]
            return jsonify({'tracks': tracks}), 200
        return jsonify({'tracks': []}), 200
    except Exception as e:
        print(f"Error fetching Robot Tour tracks: {e}")
        return jsonify({'error': str(e), 'tracks': []}), 500

@app.route('/api/robot-tour/tracks', methods=['POST'])
def save_robot_tour_tracks():
    """Save the shared Robot Tour track configs"""
    try:
        data = request.get_json()
        if not data or 'tracks' not in data:
            return jsonify({'error': 'No tracks data provided'}), 400
        payload = {
            'tracks': data['tracks'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        doc_ref = firebase_db.collection('RobotTourTracks').document(ROBOT_TOUR_DOC_ID)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(payload)
        else:
            payload['createdAt'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(payload)
        return jsonify({'id': ROBOT_TOUR_DOC_ID, 'message': 'Tracks saved successfully'}), 200
    except Exception as e:
        print(f"Error saving Robot Tour tracks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/login')
def admin_login():
    """Legacy URL: send users to the main login, then back to the admin dashboard."""
    return redirect(url_for('login') + '?redirect=' + quote('/admin/dashboard', safe=''))

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/attendance')
def admin_attendance():
    return render_template('admin_attendance.html')

@app.route('/admin/content')
def admin_content():
    return render_template('admin_content.html')

@app.route('/admin/members')
def admin_members():
    return render_template('admin_members.html')

@app.route('/admin/analytics')
def admin_analytics():
    return render_template('admin_analytics.html')

@app.route('/admin/event-placements')
def admin_event_placements():
    return render_template('admin_event_placements.html')

@app.route('/admin/house-cup')
def admin_house_cup():
    return render_template('admin_house_cup.html')

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/sponsors')
def sponsors():
    return render_template('sponsors.html')

@app.route('/templates/approved_emails.txt')
def serve_approved_emails():
    return send_from_directory('templates', 'approved_emails.txt')

# ----------------------- Practice Test PDFs -----------------------

@app.route('/practice-tests/<path:filename>')
def serve_practice_test(filename):
    """Serve practice test PDFs from Planning/nonMasonChemInqTests directory"""
    from urllib.parse import unquote
    
    # Security: Only allow PDF files and prevent directory traversal
    if not filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type'}), 400
    if '..' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # Decode URL-encoded filename (handles spaces encoded as %20)
    decoded_filename = unquote(filename)
    
    # Map URL-friendly names to actual filenames (handle spaces)
    filename_map = {
        'ChemLabPractice.pdf': 'ChemLabPractice.pdf',
        'ChemPracticeKey.pdf': 'ChemPracticeKey.pdf',
        'Codebusters-Practice-Key.pdf': 'Codebusters Practice Key.pdf',
        'Codebusters-Test.pdf': 'Codebusters Test.pdf',
        'Experimental-Design-Practice.pdf': 'Experimental Design Practice.pdf',
        'Forensics-Practice-Key.pdf': 'Forensics Practice Key.pdf',
        'Forensics-Practice-Test.pdf': 'Forensics Practice Test.pdf'
    }
    
    # Use mapped filename if available, otherwise use the decoded filename
    actual_filename = filename_map.get(filename, decoded_filename)
    
    try:
        return send_from_directory('Planning/nonMasonChemInqTests', actual_filename, mimetype='application/pdf')
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/videos/BoomiCatastrophe.mp4')
def serve_boomi_catastrophe():
    """Serve BoomiCatastrophe.mp4 video from Planning directory"""
    return send_from_directory('Planning', 'BoomiCatastrophe.mp4', mimetype='video/mp4')

# ----------------------- TopicSpace Learning -----------------------

@app.route('/api/topicspace/<event_name>')
def api_topicspace(event_name):
    """Get TopicSpace data for an event"""
    import re
    from pathlib import Path
    
    try:
        # Map event names to TopicSpace files
        topicspace_map = {
            'anatomy and physiology': 'Anatomy_Physiology_TopicSpace.txt',
            'anatomy & physiology': 'Anatomy_Physiology_TopicSpace.txt',
            'anatomy': 'Anatomy_Physiology_TopicSpace.txt',
        }
        
        event_lower = event_name.lower()
        filename = topicspace_map.get(event_lower)
        
        if not filename:
            return jsonify({'error': f'No TopicSpace found for event: {event_name}'}), 404
        
        topicspace_path = Path('TestBase/TopicSpace') / filename
        
        if not topicspace_path.exists():
            return jsonify({'error': 'TopicSpace file not found'}), 404
        
        # Parse TopicSpace file
        with open(topicspace_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse structure
        topics = []
        questions_by_topic = {}
        current_topic = None
        in_question_mapping = False
        current_test = None
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip('\n')
            line_stripped = line.strip()
            
            # Detect question mapping section FIRST (before skipping === lines)
            if 'QUESTION-TO-TOPIC MAPPING' in line_stripped or 'QUESTION-TO-TOPIC' in line_stripped:
                in_question_mapping = True
                i += 1
                continue
            
            # Skip empty lines and headers (but not question mapping section)
            if not line_stripped or (line_stripped.startswith('===') and 'QUESTION-TO-TOPIC' not in line_stripped) or line_stripped.startswith('ANATOMY & PHYSIOLOGY COMPREHENSIVE') or 'Version' in line_stripped or 'Coverage:' in line_stripped or 'Total:' in line_stripped or 'This section links' in line_stripped:
                i += 1
                continue
            
            if in_question_mapping:
                # Skip empty lines in question mapping section
                if not line_stripped:
                    i += 1
                    continue
                
                # Detect test name
                if any(x in line_stripped for x in ['HAWK & HORNET', 'UGA INVITATIONAL', 'RICKARDS', 'UT AUSTIN', 'MVSO']):
                    current_test = line_stripped
                    i += 1
                    continue
                
                # Parse question mapping: Q1 [Description] → Topic I.A (Topic Name)
                if line_stripped.startswith('Q'):
                    # Handle multiple topic references: Q1 [Desc] → Topic I.A (Name), I.B (Name2)
                    match = re.match(r'Q(\d+)(?:-Q(\d+))?\s+\[([^\]]+)\]\s*→\s*(.+)', line_stripped)
                    if match:
                        q_start = int(match.group(1))
                        q_end = int(match.group(2)) if match.group(2) else q_start
                        desc = match.group(3)
                        topics_str = match.group(4).strip()
                        
                        # Parse multiple topic references - handle both "Topic I.A (Name)" and ", I.B (Name2)" formats
                        # First, replace "Topic " at the start to make parsing consistent
                        topics_str_normalized = topics_str.replace('Topic ', '', 1).strip()
                        
                        # Now find all patterns like "I.A (Name)" or ", I.B (Name2)"
                        # Pattern: optional comma/space at start, then topic ref like I.A or II.B, then space and parentheses with name
                        topic_matches = re.findall(r'(?:^|,\s*)([IVX]+\.[A-Z]+)\s*\(([^)]+)\)', topics_str_normalized)
                        
                        if not topic_matches:
                            # Fallback: try to find topic refs without parentheses (less common)
                            topic_matches = re.findall(r'(?:^|,\s*)([IVX]+\.[A-Z]+)', topics_str_normalized)
                            topic_matches = [(ref, '') for ref in topic_matches]
                        
                        for topic_ref, topic_name in topic_matches:
                            if topic_ref not in questions_by_topic:
                                questions_by_topic[topic_ref] = []
                            
                            questions_by_topic[topic_ref].append({
                                'test': current_test,
                                'question_start': q_start,
                                'question_end': q_end,
                                'description': desc,
                                'topic_ref': topic_ref,
                                'topic_name': topic_name.strip() if topic_name else ''
                            })
                i += 1
                continue
            
            if line_stripped.startswith('END OF COMPREHENSIVE TOPIC SPACE'):
                break
            
            # Parse topic structure: I.A - Topic Name
            topic_match = re.match(r'^([IVX]+\.[A-Z]+)\s*-\s*(.+)', line_stripped)
            if topic_match:
                topic_ref = topic_match.group(1)
                topic_name = topic_match.group(2)
                
                current_topic = {
                    'ref': topic_ref,
                    'name': topic_name,
                    'subtopics': [],
                    'questions': []
                }
                topics.append(current_topic)
                i += 1
                continue
            
            # Parse subtopics (bullet points)
            if current_topic and line_stripped.startswith('•'):
                subtopic_text = line_stripped[1:].strip()
                # Skip sub-bullets (indented with -)
                if not subtopic_text.startswith('-'):
                    current_topic['subtopics'].append(subtopic_text)
            
            i += 1
        
        # Attach questions to topics
        for topic in topics:
            topic['questions'] = questions_by_topic.get(topic['ref'], [])
        
        # Debug: Print some stats
        total_questions = sum(len(q_list) for q_list in questions_by_topic.values())
        topics_with_questions = sum(1 for topic in topics if len(topic['questions']) > 0)
        
        return jsonify({
            'event': event_name,
            'topics': topics,
            'questions_by_topic': questions_by_topic,
            'stats': {
                'total_topics': len(topics),
                'topics_with_questions': topics_with_questions,
                'total_question_mappings': total_questions
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/topicspace/question/<test_name>/<int:question_id>')
def api_topicspace_question(test_name, question_id):
    """Get a specific question from a parsed test file"""
    import re
    from pathlib import Path
    
    try:
        # Map test names to file paths
        test_map = {
            'HAWK & HORNET INVITATIONAL 2026 ANATOMY & PHYSIOLOGY': 'Hawk&Hornet Invitational/TestsParsed/Hawk&Hornet Invitational 2026 Anatomy and Physiology C TEST.txt',
            'UGA INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'UGA Invitational/TestsParsed/UGA Invitational 2025 Anatomy and Physiology C TEST.txt',
            'RICKARDS INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'Rickards/TestsParsed/Rickards Invitational 2025 Anatomy and Physiology C TEST.txt',
            'UT AUSTIN INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'UTAustin/TestsParsed/UT Austin Invitational 2025 Anatomy and Physiology C TEST.txt',
            'MVSO INVITE 2025 ANATOMY & PHYSIOLOGY': 'MVSO/TestsParsed/MVSO Invite 2025 Anatomy and Physiology C TEST.txt',
        }
        
        file_path = test_map.get(test_name.upper())
        if not file_path:
            return jsonify({'error': 'Test not found'}), 404
        
        full_path = Path('TestBase') / file_path
        
        if not full_path.exists():
            return jsonify({'error': 'Test file not found'}), 404
        
        # Read and parse question
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find question
        question_pattern = rf'---QUESTION {question_id}---(.*?)(?=---QUESTION \d+---|$)'
        match = re.search(question_pattern, content, re.DOTALL)
        
        if not match:
            return jsonify({'error': 'Question not found'}), 404
        
        question_text = match.group(1).strip()
        
        # Parse question details
        question_data = {
            'id': question_id,
            'test': test_name,
            'raw_text': question_text
        }
        
        # Extract structured fields
        for field in ['ID', 'POINTS', 'FORMAT', 'TOPIC', 'DIFFICULTY', 'QUESTION', 'OPTIONS', 'CORRECT_ANSWER', 'CORRECT_ANSWERS']:
            pattern = rf'{field}:\s*(.+?)(?=\n[A-Z_]+:|$)'
            field_match = re.search(pattern, question_text, re.DOTALL | re.IGNORECASE)
            if field_match:
                value = field_match.group(1).strip()
                if field == 'OPTIONS':
                    # Parse options
                    options = []
                    for opt_match in re.finditer(r'^([A-Z])\)\s*(.+?)(?=\n[A-Z]\)|$)', value, re.MULTILINE):
                        options.append({
                            'letter': opt_match.group(1),
                            'text': opt_match.group(2).strip()
                        })
                    question_data['options'] = options
                else:
                    question_data[field.lower()] = value
        
        return jsonify(question_data), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/topicspace/pdf/<test_name>')
def api_topicspace_pdf(test_name):
    """Serve PDF for a test"""
    from pathlib import Path
    from urllib.parse import unquote
    
    try:
        # Map test names to PDF paths
        pdf_map = {
            'HAWK & HORNET INVITATIONAL 2026 ANATOMY & PHYSIOLOGY': 'Hawk&Hornet Invitational/TestsPDF/A&P_Test.pdf',
            'UGA INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'UGA Invitational/TestsPDF/A&P_Test.pdf',
            'RICKARDS INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'Rickards/TestsPDF/A&P_Test.pdf',
            'UT AUSTIN INVITATIONAL 2025 ANATOMY & PHYSIOLOGY': 'UTAustin/TestsPDF/A&P_Test.pdf',
            'MVSO INVITE 2025 ANATOMY & PHYSIOLOGY': 'MVSO/TestsPDF/MVSO Invite 2025 Anatomy and Physiology C TEST.pdf',
        }
        
        pdf_path = pdf_map.get(test_name.upper())
        if not pdf_path:
            return jsonify({'error': 'PDF not found'}), 404
        
        full_path = Path('TestBase') / pdf_path
        
        if not full_path.exists():
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Set headers to allow PDF.js and other viewers to work properly
        response = send_from_directory(str(full_path.parent), full_path.name, mimetype='application/pdf')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topicspace/pdf-page/<test_name>/<int:question_id>')
def api_topicspace_pdf_page(test_name, question_id):
    """Estimate PDF page number for a question"""
    try:
        # Rough estimation: ~2-3 questions per page on average
        # This is a heuristic - actual page numbers would need to be stored in parsed files
        estimated_page = max(1, int(question_id / 2.5))
        
        return jsonify({
            'test': test_name,
            'question_id': question_id,
            'estimated_page': estimated_page,
            'note': 'This is an estimate. Actual page numbers may vary.'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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