"""
Dashboard server for the Riyasewana scraper.
Serves a web-based dashboard that displays real-time progress.
"""
import json
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='dashboard')
CORS(app)  # Enable CORS for local development


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory('dashboard', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory('dashboard', path)


@app.route('/api/progress')
def get_progress():
    """API endpoint to get current progress."""
    progress_file = "scraper_progress.json"
    
    if not os.path.exists(progress_file):
        return jsonify({
            "status": "not_started",
            "message": "Scraper has not started yet",
        }), 200
    
    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        return jsonify(progress), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error reading progress: {str(e)}",
        }), 500


@app.route('/api/config')
def get_config():
    """API endpoint to get scraper configuration."""
    config_file = "dashboard_config.json"
    
    # Default configuration
    default_config = {
        "title": "Riyasewana Scraper Dashboard",
        "work_unit": "pages",
        "total_work": 635,
        "expected_items_per_unit": 44,
        "refresh_interval": 2000,  # milliseconds
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                default_config.update(config)
        except Exception as e:
            print(f"Warning: Could not read config file: {e}")
    
    return jsonify(default_config), 200


if __name__ == '__main__':
    # Create dashboard directory if it doesn't exist
    os.makedirs('dashboard', exist_ok=True)
    
    print("=" * 60)
    print("Riyasewana Scraper Dashboard Server")
    print("=" * 60)
    print("Dashboard available at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/progress")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

