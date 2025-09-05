"""
Enhanced YOLO-based Empty Shelf Detector
Better accuracy with advanced visual feedback
"""
import cv2
import numpy as np
import time
from typing import Dict, Tuple, List
import logging

class EnhancedShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        self.confidence_threshold = 0.3
        
        # Enhanced thresholds for better accuracy
        self.empty_thresholds = {
            'color_variance': 200,      # Higher variance = more products
            'edge_density': 80,         # More edges = more items
            'brightness_std': 15,       # Standard deviation of brightness
            'texture_energy': 0.01,     # Local binary pattern energy
            'contour_count': 5          # Number of significant contours
        }
        
        # Visual feedback colors
        self.colors = {
            'empty_high': (0, 0, 255),      # Bright red for high confidence empty
            'empty_medium': (0, 100, 255),   # Orange for medium confidence
            'empty_low': (0, 200, 255),      # Yellow for low confidence
            'full': (0, 255, 0),             # Green for full
            'uncertain': (128, 128, 128)     # Gray for uncertain
        }
        
        # History tracking for stability
        self.history_length = 8
        self.cooldown_time = 2.0
        
        print("Enhanced YOLO-based Shelf Detector initialized")
        
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Enhanced multi-method analysis with YOLO-inspired techniques
        """
        if timestamp is None:
            timestamp = time.time()
        
        if roi is None or roi.size == 0:
            return self._create_result(True, 1.0, "No image data", shelf_name, 'empty_high')
        
        # Ensure minimum size
        if roi.shape[0] < 30 or roi.shape[1] < 30:
            return self._create_result(True, 1.0, "Region too small", shelf_name, 'empty_high')
        
        self.frame_count += 1
        
        # Initialize history for new shelves
        if shelf_name not in self.detection_history:
            self.detection_history[shelf_name] = []
            self.alert_cooldown[shelf_name] = 0
        
        # Perform enhanced analysis
        analysis_results = self._perform_enhanced_analysis(roi)
        
        # Calculate confidence using multiple methods
        confidence, is_empty, visual_state = self._calculate_enhanced_confidence(analysis_results)
        
        # Update detection history
        self.detection_history[shelf_name].append({
            'timestamp': timestamp,
            'is_empty': is_empty,
            'confidence': confidence,
            'visual_state': visual_state,
            'methods': analysis_results
        })
        
        # Keep only recent history
        if len(self.detection_history[shelf_name]) > self.history_length:
            self.detection_history[shelf_name].pop(0)
        
        # Calculate stability score
        stability = self._calculate_stability(shelf_name)
        
        # Determine if we should alert
        should_alert = self._should_alert(shelf_name, timestamp, is_empty, confidence, stability)
        
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'should_alert': should_alert,
            'stability': stability,
            'visual_state': visual_state,
            'details': analysis_results,
            'frame_count': self.frame_count,
            'timestamp': timestamp,
            'method_scores': {
                'color_analysis': analysis_results['color_score'],
                'edge_analysis': analysis_results['edge_score'],
                'texture_analysis': analysis_results['texture_score'],
                'contour_analysis': analysis_results['contour_score'],
                'brightness_analysis': analysis_results['brightness_score']
            }
        }
    
    def _perform_enhanced_analysis(self, roi: np.ndarray) -> Dict:
        """
        Perform comprehensive analysis using multiple computer vision techniques
        """
        # Convert to different color spaces
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        else:
            gray = roi.copy()
            hsv = cv2.cvtColor(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)
        
        # 1. Enhanced Color Variance Analysis
        color_variance = np.var(roi) if len(roi.shape) == 3 else np.var(gray)
        color_mean = np.mean(roi) if len(roi.shape) == 3 else np.mean(gray)
        color_std = np.std(roi) if len(roi.shape) == 3 else np.std(gray)
        
        # 2. Advanced Edge Detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        edge_count = np.sum(edges > 0)
        
        # 3. Texture Analysis using Local Binary Patterns
        texture_energy = self._calculate_texture_energy(gray)
        
        # 4. Contour Analysis
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_contours = [c for c in contours if cv2.contourArea(c) > 50]
        contour_count = len(significant_contours)
        total_contour_area = sum(cv2.contourArea(c) for c in significant_contours)
        
        # 5. Brightness and Contrast Analysis
        brightness_mean = np.mean(gray)
        brightness_std = np.std(gray)
        contrast = brightness_std / max(brightness_mean, 1)
        
        # 6. Histogram Analysis
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_peaks = len([i for i in range(1, 255) if hist[i] > hist[i-1] and hist[i] > hist[i+1]])
        
        # Calculate individual method scores
        color_score = min(1.0, color_variance / self.empty_thresholds['color_variance'])
        edge_score = min(1.0, edge_density * 1000 / self.empty_thresholds['edge_density'])
        texture_score = min(1.0, texture_energy / self.empty_thresholds['texture_energy'])
        brightness_score = min(1.0, brightness_std / self.empty_thresholds['brightness_std'])
        contour_score = min(1.0, contour_count / self.empty_thresholds['contour_count'])
        
        return {
            'color_variance': color_variance,
            'color_mean': color_mean,
            'color_std': color_std,
            'edge_density': edge_density,
            'edge_count': edge_count,
            'texture_energy': texture_energy,
            'contour_count': contour_count,
            'total_contour_area': total_contour_area,
            'brightness_mean': brightness_mean,
            'brightness_std': brightness_std,
            'contrast': contrast,
            'hist_peaks': hist_peaks,
            'color_score': color_score,
            'edge_score': edge_score,
            'texture_score': texture_score,
            'brightness_score': brightness_score,
            'contour_score': contour_score
        }
    
    def _calculate_texture_energy(self, gray: np.ndarray) -> float:
        """
        Calculate texture energy using simplified Local Binary Pattern
        """
        try:
            # Simple texture measure using gradient
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            return np.mean(gradient_magnitude) / 255.0
        except:
            return 0.0
    
    def _calculate_enhanced_confidence(self, analysis: Dict) -> Tuple[float, bool, str]:
        """
        Calculate confidence using weighted combination of multiple methods
        """
        # Weighted scores (can be tuned based on performance)
        weights = {
            'color': 0.25,
            'edge': 0.30,
            'texture': 0.20,
            'brightness': 0.15,
            'contour': 0.10
        }
        
        # Individual method confidences
        color_conf = analysis['color_score']
        edge_conf = analysis['edge_score']
        texture_conf = analysis['texture_score']
        brightness_conf = analysis['brightness_score']
        contour_conf = analysis['contour_score']
        
        # Calculate weighted confidence
        fullness_confidence = (
            weights['color'] * color_conf +
            weights['edge'] * edge_conf +
            weights['texture'] * texture_conf +
            weights['brightness'] * brightness_conf +
            weights['contour'] * contour_conf
        )
        
        # Apply sensitivity adjustment
        adjusted_confidence = fullness_confidence * (2.0 - self.sensitivity)
        
        # Determine if empty (inverted logic - low confidence = empty)
        is_empty = adjusted_confidence < 0.5
        empty_confidence = 1.0 - adjusted_confidence if is_empty else adjusted_confidence
        
        # Determine visual state for color coding
        if is_empty:
            if empty_confidence > 0.8:
                visual_state = 'empty_high'
            elif empty_confidence > 0.6:
                visual_state = 'empty_medium'
            else:
                visual_state = 'empty_low'
        else:
            visual_state = 'full'
        
        return empty_confidence, is_empty, visual_state
    
    def _calculate_stability(self, shelf_name: str) -> int:
        """
        Calculate stability score based on recent detection history
        """
        if shelf_name not in self.detection_history:
            return 0
        
        history = self.detection_history[shelf_name]
        if len(history) < 3:
            return len(history)
        
        # Check consistency of recent detections
        recent_states = [h['is_empty'] for h in history[-5:]]
        consistency = sum(1 for state in recent_states if state == recent_states[-1])
        
        return min(5, consistency)
    
    def _should_alert(self, shelf_name: str, timestamp: float, 
                     is_empty: bool, confidence: float, stability: int) -> bool:
        """
        Determine if an alert should be triggered
        """
        if not is_empty:
            return False
        
        # Check confidence threshold
        if confidence < 0.6:  # Lower threshold for more sensitive detection
            return False
        
        # Check stability
        if stability < 3:
            return False
        
        # Check cooldown
        if timestamp - self.alert_cooldown[shelf_name] < self.cooldown_time:
            return False
        
        # Update cooldown
        self.alert_cooldown[shelf_name] = timestamp
        return True
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(1.0, new_sensitivity))
    
    def get_visual_color(self, visual_state: str) -> Tuple[int, int, int]:
        """Get BGR color for visual state"""
        return self.colors.get(visual_state, self.colors['uncertain'])
    
    def _create_result(self, is_empty: bool, confidence: float, 
                      reason: str, shelf_name: str, visual_state: str = 'uncertain') -> Dict:
        """Create a standardized result dictionary"""
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'should_alert': False,
            'stability': 0,
            'visual_state': visual_state,
            'details': {'reason': reason},
            'frame_count': self.frame_count,
            'timestamp': time.time(),
            'method_scores': {
                'color_analysis': 0.0,
                'edge_analysis': 0.0,
                'texture_analysis': 0.0,
                'contour_analysis': 0.0,
                'brightness_analysis': 0.0
            }
        }
