"""
Alert System Module
Handles displaying alerts, logging, and notifications
"""
import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import os

try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

class AlertSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.alert_config = config['alerts']
        self.display_config = config['display']
        self.logger = logging.getLogger(__name__)
        
        # Alert tracking
        self.active_alerts = {}
        self.alert_history = []
        
        # Setup logging if enabled
        if self.alert_config.get('log_enabled', True):
            self._setup_alert_logging()
    
    def _setup_alert_logging(self):
        """Setup file logging for alerts"""
        log_file = self.alert_config.get('log_file', 'shelf_alerts.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        alert_logger = logging.getLogger('alerts')
        alert_logger.addHandler(file_handler)
        alert_logger.setLevel(logging.INFO)
        
        self.alert_logger = alert_logger
    
    def trigger_alert(self, section_name: str, confidence: float, frame_timestamp: float = None):
        """
        Trigger an alert for an empty section
        """
        if frame_timestamp is None:
            frame_timestamp = time.time()
        
        # Check if this alert is already active (avoid spam)
        current_time = time.time()
        if section_name in self.active_alerts:
            last_alert_time = self.active_alerts[section_name]['timestamp']
            if current_time - last_alert_time < 10:  # 10 second cooldown
                return
        
        # Create alert
        alert = {
            'section': section_name,
            'confidence': confidence,
            'timestamp': current_time,
            'frame_timestamp': frame_timestamp,
            'message': f"Refill {section_name.title()} Section"
        }
        
        # Store active alert
        self.active_alerts[section_name] = alert
        
        # Add to history
        self.alert_history.append(alert.copy())
        
        # Log alert
        if hasattr(self, 'alert_logger'):
            self.alert_logger.info(f"EMPTY SHELF ALERT - Section: {section_name}, "
                                 f"Confidence: {confidence:.2f}")
        
        # Play sound if enabled
        if self.alert_config.get('sound_enabled', False) and SOUND_AVAILABLE:
            self._play_alert_sound()
        
        self.logger.info(f"Alert triggered for {section_name} section (confidence: {confidence:.2f})")
    
    def _play_alert_sound(self):
        """Play alert sound"""
        try:
            sound_file = self.alert_config.get('sound_file')
            if sound_file and os.path.exists(sound_file):
                playsound(sound_file, block=False)
            else:
                # Use system beep as fallback
                print('\a')  # ASCII bell character
        except Exception as e:
            self.logger.warning(f"Failed to play alert sound: {e}")
    
    def clear_alert(self, section_name: str):
        """Clear an active alert"""
        if section_name in self.active_alerts:
            del self.active_alerts[section_name]
    
    def draw_alerts_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw active alerts on the video frame
        """
        result = frame.copy()
        current_time = time.time()
        
        # Clean up old alerts
        expired_alerts = []
        for section_name, alert in self.active_alerts.items():
            if current_time - alert['timestamp'] > self.alert_config.get('display_duration', 3000) / 1000:
                expired_alerts.append(section_name)
        
        for section_name in expired_alerts:
            del self.active_alerts[section_name]
        
        # Draw active alerts
        y_offset = 50
        for section_name, alert in self.active_alerts.items():
            message = alert['message']
            confidence = alert['confidence']
            
            # Create alert text
            alert_text = f"⚠️ {message} (Confidence: {confidence:.0%})"
            
            # Calculate text size
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = self.display_config.get('alert_text_size', 1.0)
            thickness = self.display_config.get('alert_text_thickness', 2)
            text_size = cv2.getTextSize(alert_text, font, font_scale, thickness)[0]
            
            # Draw background rectangle
            padding = 10
            bg_x1 = 10
            bg_y1 = y_offset - text_size[1] - padding
            bg_x2 = text_size[0] + padding * 2
            bg_y2 = y_offset + padding
            
            cv2.rectangle(result, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
            cv2.rectangle(result, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 255), 2)
            
            # Draw alert text
            text_color = self.display_config.get('alert_text_color', [0, 0, 255])
            cv2.putText(result, alert_text, (bg_x1 + padding, y_offset), 
                       font, font_scale, text_color, thickness)
            
            y_offset += text_size[1] + 40  # Space between alerts
        
        return result
    
    def draw_section_status(self, frame: np.ndarray, sections: List[Dict], 
                           analysis_results: Dict) -> np.ndarray:
        """
        Draw status for each shelf section
        """
        result = frame.copy()
        
        if not self.display_config.get('show_regions', True):
            return result
        
        for section in sections:
            name = section['name']
            region = section['region']
            color = section['color']
            x, y, w, h = region
            
            # Get analysis result
            section_result = analysis_results.get(name, {})
            is_empty = section_result.get('is_empty', False)
            confidence = section_result.get('confidence', 0.0)
            
            # Choose color based on status
            if is_empty:
                box_color = (0, 0, 255)  # Red for empty
                status_text = "EMPTY"
            else:
                box_color = (0, 255, 0)  # Green for stocked
                status_text = "STOCKED"
            
            # Draw section rectangle
            cv2.rectangle(result, (x, y), (x + w, y + h), box_color, 2)
            
            # Draw section label
            label = f"{name.title()}: {status_text} ({confidence:.0%})"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            
            # Calculate text position
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            text_x = x
            text_y = y - 10 if y > 30 else y + h + 25
            
            # Draw text background
            cv2.rectangle(result, (text_x, text_y - text_size[1] - 5), 
                         (text_x + text_size[0], text_y + 5), (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(result, label, (text_x, text_y), font, font_scale, box_color, thickness)
        
        return result
    
    def get_alert_summary(self) -> Dict:
        """
        Get summary of current alerts and history
        """
        return {
            'active_alerts': len(self.active_alerts),
            'total_alerts_today': len([a for a in self.alert_history 
                                     if datetime.fromtimestamp(a['timestamp']).date() == datetime.now().date()]),
            'alert_history': self.alert_history[-10:],  # Last 10 alerts
            'sections_with_alerts': list(self.active_alerts.keys())
        }
    
    def export_alert_log(self, filename: str = None) -> str:
        """
        Export alert history to file
        """
        if filename is None:
            filename = f"alert_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w') as f:
            f.write("Shelf Monitoring Alert Log\n")
            f.write("=" * 50 + "\n\n")
            
            for alert in self.alert_history:
                timestamp = datetime.fromtimestamp(alert['timestamp'])
                f.write(f"Time: {timestamp}\n")
                f.write(f"Section: {alert['section']}\n")
                f.write(f"Message: {alert['message']}\n")
                f.write(f"Confidence: {alert['confidence']:.2f}\n")
                f.write("-" * 30 + "\n")
        
        return filename
