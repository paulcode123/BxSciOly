from flask import Flask, render_template, url_for, send_from_directory
from datetime import datetime
from routes.firebase_routes import firebase_routes
from routes.test_parsing_routes import test_parsing_routes

app = Flask(__name__)
app.register_blueprint(firebase_routes)
app.register_blueprint(test_parsing_routes)

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

@app.route('/user/conversations')
def user_conversations():
    return render_template('user/conversations.html')

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

@app.route('/user/admin/attendance')
def user_admin_attendance():
    return render_template('user/admin_attendance.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000) 