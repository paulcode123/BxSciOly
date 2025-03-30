from flask import Flask, render_template, url_for
from datetime import datetime
from routes.firebase_routes import firebase_routes

app = Flask(__name__)
app.register_blueprint(firebase_routes)

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

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/academic-events')
def academic_events():
    return render_template('academic_events.html')

@app.route('/build-events')
def build_events():
    return render_template('build_events.html')

@app.route('/biology')
def biology():
    return render_template('biology.html')

@app.route('/chemistry')
def chemistry():
    return render_template('chemistry.html')

@app.route('/earth-science')
def earth_science():
    return render_template('earth_science.html')

@app.route('/math-physics')
def math_physics():
    return render_template('math_physics.html')

@app.route('/firebase-demo')
def firebase_demo():
    return render_template('firebase_demo.html')

# User account routes
@app.route('/user/events')
def user_events():
    return render_template('user/events.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000) 