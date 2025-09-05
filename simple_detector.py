"""
Simple but Effective Empty Shelf Detector
Focuses on reliable detection with clear visual feedback
"""
import cv2
import numpy as np
import time
from typing import Dict, Tuple

class SimpleShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        
        # Simple but effective thresholds
        self.min_edge_density = 50  # Minimum edges for "not empty"
        self.min_pixel_variance = 100  # Minimum variance for "not empty"
        self.history_length = 5  # Fewer frames for faster response
        self.cooldown_time = 3.0  # Shorter cooldown
        
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Simple but reliable shelf analysis
        """
        if timestamp is None:
            timestamp = time.time()
        
        if roi is None or roi.size == 0:
            return self._create_result(True, 1.0, "No image data", shelf_name)
        
        # Ensure minimum size
        if roi.shape[0] < 20 or roi.shape[1] < 20:
            return self._create_result(True, 1.0, "Region too small", shelf_name)
        
        self.frame_count += 1
        
        # Initialize history for new shelves
        if shelf_name not in self.detection_history:
            self.detection_history[shelf_name] = []
            self.alert_cooldown[shelf_name] = 0
        
        # Convert to grayscale for analysis
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi.copy()
        
        # Method 1: Edge Detection
        edges = cv2.Canny(gray, 50, 150)
        edge_count = np.sum(edges > 0)
        edge_density = edge_count / (roi.shape[0] * roi.shape[1])
        
        # Method 2: Pixel Variance
        pixel_variance = np.var(gray)
        
        # Method 3: Histogram Analysis
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_peak = np.max(hist)
        hist_spread = np.std(hist)
        
        # Simple scoring system
        edge_score = 1.0 if edge_density > self.min_edge_density else 0.0
        variance_score = 1.0 if pixel_variance > self.min_pixel_variance else 0.0
        hist_score = 1.0 if hist_spread > 50 else 0.0
        
        # Average the scores
        fullness_score = (edge_score + variance_score + hist_score) / 3.0
        
        # Apply sensitivity
        adjusted_threshold = 0.5 + (self.sensitivity - 0.5) * 0.5
        is_empty = fullness_score < adjusted_threshold
        confidence = abs(fullness_score - 0.5) * 2  # Convert to confidence
        
        # Update history
        self.detection_history[shelf_name].append(is_empty)
        if len(self.detection_history[shelf_name]) > self.history_length:
            self.detection_history[shelf_name].pop(0)
        
        # Check stability
        recent_detections = self.detection_history[shelf_name]
        empty_count = sum(recent_detections)
        stability = len(recent_detections) - abs(len(recent_detections) - 2 * empty_count)
        
        # Determine if we should alert
        should_alert = False
        if is_empty and len(recent_detections) >= 3:
            if empty_count >= 2:  # Majority empty
                time_since_alert = timestamp - self.alert_cooldown[shelf_name]
                if time_since_alert > self.cooldown_time:
                    should_alert = True
                    self.alert_cooldown[shelf_name] = timestamp
        
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'should_alert': should_alert,
            'stability': stability,
            'method_scores': {
                'edges': edge_score,
                'variance': variance_score,
                'histogram': hist_score
            },
            'details': {
                'edge_density': edge_density,
                'pixel_variance': pixel_variance,
                'hist_spread': hist_spread,
                'fullness_score': fullness_score
            }
        }
    
    def _create_result(self, is_empty: bool, confidence: float, 
                      reason: str, shelf_name: str) -> Dict:
        """Create a standard result dictionary"""
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'should_alert': is_empty,
            'stability': 0,
            'method_scores': {},
            'details': {'reason': reason}
        }
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(0.9, new_sensitivity))
    
    def reset_shelf_history(self, shelf_name: str = None):
        """Reset detection history for a shelf or all shelves"""
        if shelf_name:
            if shelf_name in self.detection_history:
                self.detection_history[shelf_name] = []
                self.alert_cooldown[shelf_name] = 0
        else:
            self.detection_history.clear()
            self.alert_cooldown.clear()
    
    def get_shelf_stats(self, shelf_name: str) -> Dict:
        """Get statistics for a specific shelf"""
        if shelf_name not in self.detection_history:
            return {'history_length': 0, 'empty_percentage': 0}
        
        history = self.detection_history[shelf_name]
        empty_count = sum(history)
        
        return {
            'history_length': len(history),
            'empty_count': empty_count,
            'empty_percentage': (empty_count / len(history)) * 100 if history else 0,
            'last_alert': self.alert_cooldown.get(shelf_name, 0)
        }
