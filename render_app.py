"""
Flask Web API for Shelf Monitoring System
Headless deployment for Render and cloud platforms
"""
import os
import sys

# Fix YOLO config directory for Render
os.environ['YOLO_CONFIG_DIR'] = '/tmp/ultralytics'

from flask import Flask, jsonify, request, render_template, send_file
from main import ShelfMonitoringSystem
import threading
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Create templates and static directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Global monitoring state
monitoring_state = {
    'is_running': False,
    'frame_count': 0,
    'alerts': [],
    'empty_shelves': 0
}

# ==================== Web Routes ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

# ==================== API Endpoints ====================

@app.route('/api', methods=['GET'])
def api_home():
    """API Status endpoint"""
    return jsonify({
        'status': 'Shelf Monitoring API is running',
        'version': '1.0',
        'environment': 'Render Cloud',
        'endpoints': {
            'dashboard': '/',
            'status': '/api/status',
            'start': '/api/start',
            'stop': '/api/stop',
            'alerts': '/api/alerts',
            'health': '/api/health'
        }
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current monitoring status"""
    return jsonify({
        'is_running': monitoring_state['is_running'],
        'frame_count': monitoring_state['frame_count'],
        'empty_shelves': monitoring_state['empty_shelves'],
        'alerts_count': len(monitoring_state['alerts']),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts"""
    limit = request.args.get('limit', default=10, type=int)
    return jsonify({
        'alerts': monitoring_state['alerts'][-limit:],
        'total': len(monitoring_state['alerts'])
    })

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start monitoring service"""
    try:
        if monitoring_state['is_running']:
            return jsonify({'error': 'Monitoring already running'}), 400
        
        # Get video source from request
        data = request.get_json() or {}
        video_source = data.get('video_source', 0)  # Default: camera
        output_path = data.get('output_path', '/tmp/monitored_output.mp4')  # Use /tmp for Render
        
        # Start monitoring in background thread
        monitoring_state['is_running'] = True
        monitoring_state['frame_count'] = 0
        monitoring_state['alerts'] = []
        monitoring_state['empty_shelves'] = 0
        
        monitor_thread = threading.Thread(
            target=run_monitoring,
            args=(video_source, output_path),
            daemon=True
        )
        monitor_thread.start()
        
        return jsonify({
            'status': 'Monitoring started',
            'video_source': str(video_source),
            'output_path': output_path,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        monitoring_state['is_running'] = False
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring service"""
    monitoring_state['is_running'] = False
    return jsonify({
        'status': 'Monitoring stopped',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Shelf Monitoring API',
        'version': '1.0',
        'environment': 'Render Cloud',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== Background Monitoring ====================

def run_monitoring(video_source, output_path):
    """Background monitoring thread"""
    try:
        # Add alert about monitoring start
        monitoring_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'INFO',
            'message': f'Starting monitoring from source: {video_source}'
        })
        
        monitor = ShelfMonitoringSystem()
        
        # Check if monitoring should continue
        while monitoring_state['is_running']:
            try:
                if isinstance(video_source, str) and video_source != '0':
                    # Video file processing
                    if Path(video_source).exists():
                        monitor.process_video_file(video_source, output_path)
                        monitoring_state['alerts'].append({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'SUCCESS',
                            'message': f'Video processing completed: {output_path}'
                        })
                    else:
                        monitoring_state['alerts'].append({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'ERROR',
                            'message': f'Video file not found: {video_source}'
                        })
                else:
                    # Real-time camera monitoring
                    monitoring_state['alerts'].append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'INFO',
                        'message': 'Camera monitoring mode (limited in cloud)'
                    })
                    break
                    
            except Exception as loop_error:
                monitoring_state['alerts'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'WARNING',
                    'message': f'Monitoring error: {str(loop_error)}'
                })
                break
            
    except Exception as e:
        monitoring_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'ERROR',
            'message': f'Monitoring failed: {str(e)}'
        })
    finally:
        monitoring_state['is_running'] = False
        monitoring_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'INFO',
            'message': 'Monitoring session ended'
        })

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.before_request
def log_request():
    """Log incoming requests"""
    print(f"[{datetime.now().isoformat()}] {request.method} {request.path}")

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting Flask app on port {port}...")
    print(f"YOLO_CONFIG_DIR: {os.environ.get('YOLO_CONFIG_DIR', 'default')}")
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
