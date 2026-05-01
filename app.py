"""
Root-level entry point for cloud deployment.
The dashboard runs standalone - violations data is loaded from environment
or seeded with demo data when no local session is active.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dashboard.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
