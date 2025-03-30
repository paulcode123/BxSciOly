# Bronx Science Olympiad Website

A Flask web application for the Bronx Science Olympiad team, showcasing information about the team, events, and providing resources for members.

## Features

- Home page with promotional content about Science Olympiad
- Academic Events page with detailed information about academic events
- Build Events page with detailed information about build events
- Responsive design for desktop and mobile devices

## Prerequisites

- Python 3.7 or higher
- Flask 2.3.3 or higher

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/BxSciOly.git
cd BxSciOly
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS and Linux:
   ```
   source venv/bin/activate
   ```

4. Install the required packages:
```
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```
python app.py
```

2. Open a web browser and go to `http://127.0.0.1:5000/`

## Project Structure

- `app.py` - Main Flask application file
- `templates/` - HTML templates
  - `layout.html` - Base layout template
  - `index.html` - Home page template
  - `academic_events.html` - Academic events page template
  - `build_events.html` - Build events page template
- `static/` - Static files
  - `css/` - CSS stylesheets
  - `js/` - JavaScript files
  - `images/` - Image files

## Notes

- The application is set to run in debug mode by default for development purposes. For production deployment, it is recommended to use a production WSGI server like Gunicorn or uWSGI.
- You will need to add your own images to the `static/images/` directory (earth.jpg for the hero background and logo.png for the Bronx Science logo).

## License

This project is licensed under the MIT License - see the LICENSE file for details. 