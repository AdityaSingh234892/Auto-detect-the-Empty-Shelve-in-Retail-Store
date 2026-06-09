"""
Flask Web API for Shelf Monitoring System
Headless deployment for Render and cloud platforms
"""
import os
import sys

# Fix YOLO config directory for Render
os.environ['YOLO_CONFIG_DIR'] = '/tmp/ultralytics'

from flask import Flask, jsonify, request
from main import ShelfMonitoringSystem
import threading
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Global monitoring state
monitoring_state = {
    'is_running': False,
    'frame_count': 0,
    'alerts': [],
    'empty_shelves': 0
}

# ==================== HTML Dashboard ====================

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Shelf Monitor Pro - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3d3d3d;
            --accent: #0078d4;
            --success: #107c10;
            --warning: #ffb900;
            --danger: #d13438;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --border-color: #404040;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            padding: 40px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .header-content h1 {
            font-size: 2.5em;
            margin-bottom: 5px;
            background: linear-gradient(135deg, #0078d4, #107c10);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-content .subtitle {
            color: var(--text-secondary);
            font-size: 1.1em;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background-color: var(--bg-tertiary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .status-dot {
            width: 12px;
            height: 12px;
            background-color: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .status-dot.inactive {
            background-color: var(--warning);
        }

        .status-text {
            font-weight: 600;
            color: var(--text-primary);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .main-content {
            flex: 1;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        section {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        section h2 {
            margin-bottom: 20px;
            font-size: 1.5em;
            color: var(--text-primary);
            border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
        }

        .control-panel { grid-column: 1 / -1; }

        .control-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: flex-end;
        }

        .input-group {
            display: flex;
            flex-direction: column;
        }

        .input-group label {
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .input-group select,
        .input-group input[type="file"] {
            padding: 10px 12px;
            background-color: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.95em;
            transition: all 0.3s ease;
        }

        .input-group select:focus,
        .input-group input[type="file"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.2);
        }

        .button-group {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
        }

        .btn-success {
            background-color: var(--success);
            color: white;
        }

        .btn-success:hover:not(:disabled) {
            background-color: #0a7a0a;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 124, 16, 0.3);
        }

        .btn-danger {
            background-color: var(--danger);
            color: white;
        }

        .btn-danger:hover:not(:disabled) {
            background-color: #b91f26;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(209, 52, 56, 0.3);
        }

        .btn-info {
            background-color: var(--accent);
            color: white;
        }

        .btn-info:hover {
            background-color: #005fa3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .stat-card {
            background-color: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0, 120, 212, 0.2);
        }

        .stat-icon {
            font-size: 2.5em;
            min-width: 50px;
            text-align: center;
        }

        .stat-info {
            flex: 1;
        }

        .stat-label {
            font-size: 0.85em;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--accent);
        }

        .alerts-panel { grid-column: 1 / -1; }

        .alerts-container {
            max-height: 500px;
            overflow-y: auto;
        }

        .alert-item {
            background-color: var(--bg-tertiary);
            border-left: 4px solid var(--accent);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }

        .alert-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .alert-item.critical { border-left-color: var(--danger); }
        .alert-item.warning { border-left-color: var(--warning); }
        .alert-item.success { border-left-color: var(--success); }

        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .alert-type {
            font-weight: 600;
            font-size: 1em;
        }

        .alert-time {
            font-size: 0.85em;
            color: var(--text-secondary);
        }

        .alert-message {
            color: var(--text-secondary);
            font-size: 0.95em;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-secondary);
        }

        .api-status-panel { grid-column: 1 / -1; }

        .api-info {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .api-endpoint {
            background-color: var(--bg-tertiary);
            padding: 15px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }

        .endpoint-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .api-endpoint code {
            display: block;
            background-color: var(--bg-primary);
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: var(--accent);
            word-break: break-all;
            font-size: 0.9em;
        }

        .api-buttons {
            display: flex;
            gap: 10px;
        }

        .api-buttons .btn {
            flex: 1;
        }

        .footer {
            text-align: center;
            padding: 20px;
            border-top: 1px solid var(--border-color);
            margin-top: auto;
            color: var(--text-secondary);
        }

        .footer p {
            margin: 5px 0;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header { flex-direction: column; text-align: center; gap: 20px; }
            .header-content h1 { font-size: 1.8em; }
            .main-content { grid-template-columns: 1fr; }
            .control-group { grid-template-columns: 1fr; }
            .button-group { flex-direction: column; }
            .stat-card { justify-content: space-between; }
            .api-buttons { flex-direction: column; }
            .alerts-container { max-height: 400px; }
        }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-tertiary); }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1>🛒 Smart Shelf Monitor Pro</h1>
                <p class="subtitle">Real-time Empty Shelf Detection System</p>
            </div>
            <div class="status-indicator" id="statusIndicator">
                <span class="status-dot"></span>
                <span class="status-text">Ready</span>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Control Panel -->
            <section class="control-panel">
                <h2>📋 Control Panel</h2>
                <div class="control-group">
                    <div class="input-group">
                        <label for="videoSource">Video Source:</label>
                        <select id="videoSource" onchange="onSourceChange()">
                            <option value="0">Camera (Webcam)</option>
                            <option value="file">Video File</option>
                        </select>
                    </div>

                    <div class="input-group" id="fileInputGroup" style="display: none;">
                        <label for="videoFile">Select Video File:</label>
                        <input type="file" id="videoFile" accept="video/*">
                    </div>

                    <div class="button-group">
                        <button id="startBtn" class="btn btn-success" onclick="startMonitoring()">
                            ▶️ Start Monitoring
                        </button>
                        <button id="stopBtn" class="btn btn-danger" onclick="stopMonitoring()" disabled>
                            ⏹️ Stop Monitoring
                        </button>
                    </div>
                </div>
            </section>

            <!-- Statistics Panel -->
            <section class="stats-panel">
                <h2>📊 Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">📍</div>
                        <div class="stat-info">
                            <div class="stat-label">Status</div>
                            <div class="stat-value" id="statusValue">Idle</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">📦</div>
                        <div class="stat-info">
                            <div class="stat-label">Empty Shelves</div>
                            <div class="stat-value" id="emptyShelvesValue">0</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">🚨</div>
                        <div class="stat-info">
                            <div class="stat-label">Total Alerts</div>
                            <div class="stat-value" id="alertsCountValue">0</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">⏱️</div>
                        <div class="stat-info">
                            <div class="stat-label">Uptime</div>
                            <div class="stat-value" id="uptimeValue">00:00:00</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Alerts Panel -->
            <section class="alerts-panel">
                <h2>🚨 Recent Alerts</h2>
                <div class="alerts-container" id="alertsContainer">
                    <div class="empty-state">
                        <p>No alerts yet. System is monitoring...</p>
                    </div>
                </div>
            </section>

            <!-- API Status -->
            <section class="api-status-panel">
                <h2>🔧 API Status</h2>
                <div class="api-info">
                    <div class="api-endpoint">
                        <span class="endpoint-label">API Base URL:</span>
                        <code id="apiUrl">Loading...</code>
                    </div>
                    <div class="api-buttons">
                        <button class="btn btn-info" onclick="checkHealth()">🏥 Health Check</button>
                        <button class="btn btn-info" onclick="refreshStatus()">🔄 Refresh</button>
                    </div>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <p>&copy; 2026 Smart Shelf Monitor Pro. All rights reserved.</p>
            <p class="footer-note">Powered by OpenCV, YOLO, and Flask</p>
        </footer>
    </div>

    <script>
        const API_BASE_URL = window.location.origin;
        let monitoringActive = false;
        let monitoringStartTime = null;
        let uptimeInterval = null;

        document.addEventListener('DOMContentLoaded', () => {
            console.log('Dashboard loaded');
            document.getElementById('apiUrl').textContent = API_BASE_URL;
            refreshStatus();
            setInterval(() => {
                if (monitoringActive) refreshStatus();
            }, 3000);
        });

        function onSourceChange() {
            const source = document.getElementById('videoSource').value;
            const fileInputGroup = document.getElementById('fileInputGroup');
            fileInputGroup.style.display = source === 'file' ? 'block' : 'none';
        }

        async function startMonitoring() {
            try {
                const source = document.getElementById('videoSource').value;
                const payload = {};

                if (source === 'file') {
                    const fileInput = document.getElementById('videoFile');
                    if (!fileInput.files.length) {
                        alert('Please select a video file');
                        return;
                    }
                    payload.video_source = fileInput.files[0].name;
                } else {
                    payload.video_source = 0;
                }

                payload.output_path = '/tmp/monitored_output.mp4';

                const response = await fetch(`${API_BASE_URL}/api/start`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error('Failed to start monitoring');

                monitoringActive = true;
                monitoringStartTime = Date.now();
                updateUIState();
                startUptimeCounter();
                showAlert('✅ Monitoring started successfully!', 'success');
            } catch (error) {
                console.error('Error:', error);
                showAlert('❌ Failed to start monitoring: ' + error.message, 'danger');
            }
        }

        async function stopMonitoring() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/stop`, { method: 'POST' });
                if (!response.ok) throw new Error('Failed to stop monitoring');

                monitoringActive = false;
                clearInterval(uptimeInterval);
                updateUIState();
                showAlert('⏹️ Monitoring stopped', 'warning');
            } catch (error) {
                console.error('Error:', error);
                showAlert('❌ Failed to stop monitoring: ' + error.message, 'danger');
            }
        }

        function updateUIState() {
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            const statusValue = document.getElementById('statusValue');

            if (monitoringActive) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusDot.classList.remove('inactive');
                statusText.textContent = 'Monitoring';
                statusValue.textContent = 'Active';
                statusValue.style.color = '#107c10';
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusDot.classList.add('inactive');
                statusText.textContent = 'Ready';
                statusValue.textContent = 'Idle';
                statusValue.style.color = '#0078d4';
            }
        }

        async function refreshStatus() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/status`);
                if (!response.ok) throw new Error('Failed to fetch status');
                const data = await response.json();
                document.getElementById('emptyShelvesValue').textContent = data.empty_shelves || 0;
                document.getElementById('alertsCountValue').textContent = data.alerts_count || 0;
                fetchAlerts();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function fetchAlerts() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/alerts?limit=10`);
                if (!response.ok) throw new Error('Failed to fetch alerts');
                const data = await response.json();
                displayAlerts(data.alerts || []);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayAlerts(alerts) {
            const container = document.getElementById('alertsContainer');
            if (!alerts || alerts.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No alerts yet. System is monitoring...</p></div>';
                return;
            }
            container.innerHTML = alerts.map(alert => {
                const alertType = alert.type || 'INFO';
                const alertClass = alertType === 'ERROR' ? 'critical' : alertType === 'WARNING' ? 'warning' : 'success';
                const timestamp = new Date(alert.timestamp).toLocaleTimeString();
                return `<div class="alert-item ${alertClass}"><div class="alert-header"><span class="alert-type">${alertType}</span><span class="alert-time">${timestamp}</span></div><div class="alert-message">${alert.message || 'No message'}</div></div>`;
            }).join('');
        }

        async function checkHealth() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/health`);
                if (!response.ok) throw new Error('Health check failed');
                const data = await response.json();
                showAlert('✅ API is healthy!', 'success');
            } catch (error) {
                console.error('Error:', error);
                showAlert('❌ API health check failed', 'danger');
            }
        }

        function showAlert(message, type = 'info') {
            const alert = document.createElement('div');
            const colors = {
                'success': '#107c10',
                'danger': '#d13438',
                'warning': '#ffb900',
                'info': '#0078d4'
            };
            alert.style.cssText = `position: fixed; top: 20px; right: 20px; padding: 15px 20px; border-radius: 8px; color: white; font-weight: 600; z-index: 1000; animation: slideIn 0.3s ease-out; background-color: ${colors[type] || colors['info']};`;
            alert.textContent = message;
            document.body.appendChild(alert);
            setTimeout(() => {
                alert.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => alert.remove(), 300);
            }, 4000);
        }

        function startUptimeCounter() {
            uptimeInterval = setInterval(() => {
                if (!monitoringStartTime) return;
                const elapsed = Date.now() - monitoringStartTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                const uptimeText = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                document.getElementById('uptimeValue').textContent = uptimeText;
            }, 1000);
        }

        const style = document.createElement('style');
        style.textContent = `@keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } } @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(400px); opacity: 0; } }`;
        document.head.appendChild(style);
    </script>
</body>
</html>
'''

# ==================== Web Routes ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the main dashboard"""
    return DASHBOARD_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

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
        
        data = request.get_json() or {}
        video_source = data.get('video_source', 0)
        output_path = data.get('output_path', '/tmp/monitored_output.mp4')
        
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
        monitoring_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'INFO',
            'message': f'Starting monitoring from source: {video_source}'
        })
        
        monitor = ShelfMonitoringSystem()
        
        while monitoring_state['is_running']:
            try:
                if isinstance(video_source, str) and video_source != '0':
                    if Path(video_source).exists():
                        monitor.process_video_file(video_source, output_path)
                        monitoring_state['alerts'].append({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'SUCCESS',
                            'message': f'Video processing completed'
                        })
                    else:
                        monitoring_state['alerts'].append({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'ERROR',
                            'message': f'Video file not found: {video_source}'
                        })
                else:
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
