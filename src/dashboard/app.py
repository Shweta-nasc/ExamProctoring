import os
import json
import sys
import yaml
from flask import Flask, render_template, jsonify, send_file, abort
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# ── Config loading (works locally and on cloud) ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

LOG_PATH        = config['logging']['log_path']
VIOLATIONS_FILE = os.path.join(config['global']['output_path'], 'violations.json')
REPORTS_DIR     = config['reporting']['output_dir']

sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

# ── Demo data for cloud/hackathon presentation ──
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

def _demo_violations():
    """Generate realistic demo violations for presentation"""
    types = [
        'FACE_DISAPPEARED', 'MULTIPLE_FACES', 'OBJECT_DETECTED',
        'MOUTH_MOVING', 'GAZE_AWAY', 'AUDIO_DETECTED'
    ]
    base = datetime.now() - timedelta(minutes=30)
    violations = []
    for i in range(18):
        ts = base + timedelta(minutes=i * 1.7)
        violations.append({
            'type': random.choice(types),
            'timestamp': ts.strftime("%Y%m%d_%H%M%S_%f"),
            'metadata': {'duration': '5+ seconds'}
        })
    return violations

def _demo_alerts():
    msgs = [
        "2026-04-25 10:01:12 - FACE_DISAPPEARED: Face disappeared for more than 5 seconds",
        "2026-04-25 10:03:44 - MULTIPLE_FACES: Detected 2 faces for 6 frames",
        "2026-04-25 10:07:20 - OBJECT_DETECTED: Unauthorized object detected",
        "2026-04-25 10:11:05 - MOUTH_MOVEMENT: Excessive mouth movement detected",
        "2026-04-25 10:14:33 - GAZE_AWAY: Excessive eye movement detected",
        "2026-04-25 10:18:50 - AUDIO_DETECTED: Voice activity detected",
        "2026-04-25 10:22:17 - FACE_DISAPPEARED: Face disappeared for more than 5 seconds",
        "2026-04-25 10:25:09 - OBJECT_DETECTED: Unauthorized object detected",
    ]
    return msgs

def _load_violations():
    if DEMO_MODE:
        return _demo_violations()
    if os.path.exists(VIOLATIONS_FILE):
        with open(VIOLATIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def _load_alerts():
    if DEMO_MODE:
        return _demo_alerts()
    log_file = os.path.join(LOG_PATH, 'alerts.log')
    alerts = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f.readlines()[-20:]:
                line = line.strip()
                if line:
                    alerts.append(line)
    return alerts


# ── Routes ──

@app.route('/')
def dashboard():
    return render_template('dashboard.html', demo_mode=DEMO_MODE)


@app.route('/api/alerts')
def get_alerts():
    return jsonify(_load_alerts())


@app.route('/api/violations')
def get_violations():
    return jsonify(_load_violations())


@app.route('/api/stats')
def get_stats():
    violations = _load_violations()

    severity_map = {
        'FACE_DISAPPEARED': 1, 'GAZE_AWAY': 2, 'MOUTH_MOVING': 3,
        'MOUTH_MOVEMENT': 3,   'MULTIPLE_FACES': 4, 'OBJECT_DETECTED': 5,
        'AUDIO_DETECTED': 3
    }

    by_type = {}
    for v in violations:
        t = v.get('type', 'UNKNOWN')
        by_type[t] = by_type.get(t, 0) + 1

    score = sum(severity_map.get(v.get('type', ''), 1) for v in violations)
    risk  = 'High' if score >= 10 else 'Medium' if score > 0 else 'Low'

    return jsonify({
        'total_violations': len(violations),
        'by_type': by_type,
        'risk_level': risk,
        'severity_score': score,
        'last_updated': datetime.now().strftime("%H:%M:%S"),
        'demo_mode': DEMO_MODE
    })


@app.route('/api/reports')
def get_reports():
    reports = []
    if os.path.exists(REPORTS_DIR):
        for f in os.listdir(REPORTS_DIR):
            if f.endswith('.pdf') or f.endswith('.html'):
                full = os.path.join(REPORTS_DIR, f)
                reports.append({
                    'name': f,
                    'created': datetime.fromtimestamp(
                        os.path.getctime(full)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                })
    return jsonify(sorted(reports, key=lambda x: x['created'], reverse=True))


@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        from reporting.report_generator import ReportGenerator

        violations = _load_violations()
        if not violations:
            return jsonify({'error': 'No violations data found. Run the monitoring system first.'}), 400

        student_info = {
            'id': 'STUDENT_001',
            'name': 'John Doe',
            'exam': 'Final Examination',
            'course': 'Computer Science 101'
        }

        os.makedirs(REPORTS_DIR, exist_ok=True)
        rg = ReportGenerator(config)
        report_path = rg.generate_report(student_info, violations, output_format='html')

        if report_path:
            return jsonify({'success': True, 'path': os.path.basename(report_path)})
        return jsonify({'error': 'Report generation failed.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reports/download/<filename>')
def download_report(filename):
    filepath = os.path.join(os.path.abspath(REPORTS_DIR), filename)
    if not os.path.exists(filepath):
        abort(404)
    if filename.endswith('.html'):
        return send_file(filepath, mimetype='text/html')
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    os.makedirs(LOG_PATH, exist_ok=True)
    os.makedirs(config['global']['output_path'], exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    print(f"\n✅ Dashboard running at: http://localhost:{port}")
    print(f"   Demo mode: {DEMO_MODE}\n")
    app.run(debug=debug, host='0.0.0.0', port=port)
