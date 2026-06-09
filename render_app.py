"""
Flask Web API for Shelf Monitoring System
Headless deployment for Render and cloud platforms
"""
import os
from flask import Flask, jsonify, request, send_file
from main import ShelfMonitoringSystem
import threading
import json
from datetime import datetime

app = Flask(__name__)

# Global monitoring state
monitoring_state = {
    'is_running': False,
    'frame_count': 0,
    'alerts': [],
    'empty_shelves': 0
}

@app.route('/', methods=['GET'])
def home():
    """API Status endpoint"""
    return jsonify({
        'status': 'Shelf Monitoring API is running',
        'version': '1.0',
        'endpoints': {
            'status': '/api/status',
            'start': '/api/start',
            'stop': '/api/stop',
            'alerts': '/api/alerts'
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
        output_path = data.get('output_path', 'monitored_output.mp4')
        
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
            'video_source': video_source,
            'output_path': output_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring service"""
    monitoring_state['is_running'] = False
    return jsonify({'status': 'Monitoring stopped'})

def run_monitoring(video_source, output_path):
    """Background monitoring thread"""
    try:
        monitor = ShelfMonitoringSystem()
        
        if isinstance(video_source, str):
            # Video file processing
            monitor.process_video_file(video_source, output_path)
        else:
            # Real-time camera monitoring
            monitor.run_realtime()
            
    except Exception as e:
        monitoring_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'ERROR',
            'message': str(e)
        })
    finally:
        monitoring_state['is_running'] = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
