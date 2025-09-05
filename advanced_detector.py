"""
Enhanced Detection System for Modern GUI
Advanced shelf monitoring with multiple detection methods
"""
import cv2
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
import logging

class AdvancedShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}  # Store detection history for each shelf
        self.alert_cooldown = {}     # Prevent alert spam
        self.frame_count = 0
        
        # Detection parameters
        self.empty_threshold = 1.0 - sensitivity  # Invert sensitivity for threshold
        self.confidence_threshold = 0.8
        self.history_length = 10  # Frames to consider for stability
        self.cooldown_time = 5.0  # Seconds between alerts for same shelf
        
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Analyze a shelf region using multiple detection methods
        
        Args:
            roi: Region of interest (shelf area)
            shelf_name: Name identifier for the shelf
            timestamp: Current timestamp
            
        Returns:
            Dictionary with detection results
        """
        if timestamp is None:
            timestamp = time.time()
        
        if roi is None or roi.size == 0:
            return self._create_result(True, 1.0, "No ROI data", shelf_name)
        
        self.frame_count += 1
        
        # Initialize history for new shelves
        if shelf_name not in self.detection_history:
            self.detection_history[shelf_name] = []
            self.alert_cooldown[shelf_name] = 0
        
        # Method 1: Pixel Variance Analysis
        variance_score = self._analyze_pixel_variance(roi)
        
        # Method 2: Edge Density Analysis
        edge_score = self._analyze_edge_density(roi)
        
        # Method 3: Color Histogram Analysis
        color_score = self._analyze_color_distribution(roi)
        
        # Method 4: Texture Analysis
        texture_score = self._analyze_texture_patterns(roi)
        
        # Method 5: Contour Analysis
        contour_score = self._analyze_contours(roi)
        
        # Combine all scores with weights
        weights = [0.25, 0.25, 0.20, 0.15, 0.15]  # Adjust based on importance
        scores = [variance_score, edge_score, color_score, texture_score, contour_score]
        
        combined_score = sum(w * s for w, s in zip(weights, scores))
        
        # Apply sensitivity adjustment
        adjusted_score = self._apply_sensitivity(combined_score)
        
        # Determine if empty based on threshold
        is_empty = adjusted_score > self.empty_threshold
        
        # Add to history for temporal consistency
        self.detection_history[shelf_name].append({
            'timestamp': timestamp,
            'is_empty': is_empty,
            'confidence': adjusted_score,
            'scores': {
                'variance': variance_score,
                'edge': edge_score,
                'color': color_score,
                'texture': texture_score,
                'contour': contour_score
            }
        })
        
        # Keep only recent history
        if len(self.detection_history[shelf_name]) > self.history_length:
            self.detection_history[shelf_name].pop(0)
        
        # Get stable result based on recent history
        stable_result = self._get_stable_result(shelf_name)
        
        # Check alert cooldown
        should_alert = (stable_result['is_empty'] and 
                       timestamp - self.alert_cooldown[shelf_name] > self.cooldown_time)
        
        if should_alert:
            self.alert_cooldown[shelf_name] = timestamp
        
        return {
            'is_empty': stable_result['is_empty'],
            'confidence': stable_result['confidence'],
            'should_alert': should_alert,
            'method_scores': stable_result['scores'],
            'stability': len(self.detection_history[shelf_name]),
            'analysis_details': self._create_analysis_details(roi, scores)
        }
    
    def _analyze_pixel_variance(self, roi: np.ndarray) -> float:
        """Analyze pixel intensity variance"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Calculate local variance using a sliding window
        kernel = np.ones((5, 5), np.float32) / 25
        mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        sqr_mean = cv2.filter2D((gray.astype(np.float32))**2, -1, kernel)
        variance = sqr_mean - mean**2
        
        # Empty shelves have low variance (uniform appearance)
        avg_variance = np.mean(variance)
        max_variance = 2000  # Empirical maximum
        
        # Normalize and invert (high score = likely empty)
        normalized_score = 1.0 - min(avg_variance / max_variance, 1.0)
        return normalized_score
    
    def _analyze_edge_density(self, roi: np.ndarray) -> float:
        """Analyze edge density in the region"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges using Canny
        edges = cv2.Canny(blurred, 30, 100)
        
        # Calculate edge density
        total_pixels = gray.shape[0] * gray.shape[1]
        edge_pixels = np.sum(edges > 0)
        edge_density = edge_pixels / total_pixels
        
        # Empty shelves have fewer edges
        max_density = 0.15  # Empirical maximum
        normalized_score = 1.0 - min(edge_density / max_density, 1.0)
        
        return normalized_score
    
    def _analyze_color_distribution(self, roi: np.ndarray) -> float:
        """Analyze color distribution uniformity"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms for each channel
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
        
        # Calculate histogram concentration (peaks)
        def calculate_concentration(hist):
            total = np.sum(hist)
            if total == 0:
                return 1.0
            
            # Find the dominant bins
            sorted_indices = np.argsort(hist.flatten())[::-1]
            top_10_percent = int(len(sorted_indices) * 0.1)
            dominant_sum = np.sum(hist.flatten()[sorted_indices[:top_10_percent]])
            
            return dominant_sum / total
        
        h_concentration = calculate_concentration(hist_h)
        s_concentration = calculate_concentration(hist_s)
        v_concentration = calculate_concentration(hist_v)
        
        # Empty shelves have more concentrated color distributions
        avg_concentration = (h_concentration + s_concentration + v_concentration) / 3
        
        # Normalize to 0-1 range where 1 = likely empty
        return min(avg_concentration * 1.2, 1.0)
    
    def _analyze_texture_patterns(self, roi: np.ndarray) -> float:
        """Analyze texture patterns using Local Binary Patterns"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate texture measures
        texture_std = np.std(gradient_magnitude)
        texture_mean = np.mean(gradient_magnitude)
        
        # Empty shelves have low texture variation
        texture_score = texture_std + texture_mean * 0.1
        max_texture = 50  # Empirical maximum
        
        normalized_score = 1.0 - min(texture_score / max_texture, 1.0)
        return normalized_score
    
    def _analyze_contours(self, roi: np.ndarray) -> float:
        """Analyze contour patterns in the region"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 1.0  # No contours = likely empty
        
        # Analyze contour properties
        total_area = roi.shape[0] * roi.shape[1]
        contour_areas = [cv2.contourArea(c) for c in contours]
        
        # Calculate contour density and complexity
        total_contour_area = sum(contour_areas)
        contour_density = total_contour_area / total_area
        contour_count = len(contours)
        
        # Empty shelves have fewer, simpler contours
        complexity_score = (contour_count * 0.1 + contour_density) / 2
        max_complexity = 0.5  # Empirical maximum
        
        normalized_score = 1.0 - min(complexity_score / max_complexity, 1.0)
        return normalized_score
    
    def _apply_sensitivity(self, score: float) -> float:
        """Apply sensitivity adjustment to the combined score"""
        # Sensitivity affects how easily we detect empty shelves
        # High sensitivity = more likely to detect as empty
        sensitivity_factor = (self.sensitivity - 0.5) * 0.4  # Range: -0.2 to 0.2
        adjusted_score = score + sensitivity_factor
        
        return max(0.0, min(1.0, adjusted_score))
    
    def _get_stable_result(self, shelf_name: str) -> Dict:
        """Get stable result based on recent detection history"""
        history = self.detection_history[shelf_name]
        
        if not history:
            return {'is_empty': False, 'confidence': 0.0, 'scores': {}}
        
        # Calculate weighted average (recent detections have more weight)
        weights = np.linspace(0.5, 1.0, len(history))
        weights = weights / np.sum(weights)
        
        # Weighted average of confidence scores
        confidences = [h['confidence'] for h in history]
        avg_confidence = np.average(confidences, weights=weights)
        
        # Majority vote for emptiness (with recency bias)
        empty_votes = [h['is_empty'] for h in history]
        weighted_votes = np.average([1.0 if v else 0.0 for v in empty_votes], weights=weights)
        
        is_empty = weighted_votes > 0.5
        
        # Average method scores
        method_scores = {}
        if history[-1]['scores']:
            for method in history[-1]['scores']:
                scores = [h['scores'][method] for h in history if method in h['scores']]
                method_scores[method] = np.mean(scores) if scores else 0.0
        
        return {
            'is_empty': is_empty,
            'confidence': avg_confidence,
            'scores': method_scores
        }
    
    def _create_analysis_details(self, roi: np.ndarray, scores: List[float]) -> Dict:
        """Create detailed analysis information"""
        return {
            'roi_size': roi.shape if roi is not None else (0, 0),
            'mean_intensity': float(np.mean(roi)) if roi is not None else 0.0,
            'std_intensity': float(np.std(roi)) if roi is not None else 0.0,
            'method_scores': {
                'variance': scores[0],
                'edge': scores[1],
                'color': scores[2],
                'texture': scores[3],
                'contour': scores[4]
            },
            'frame_count': self.frame_count
        }
    
    def _create_result(self, is_empty: bool, confidence: float, 
                      reason: str, shelf_name: str) -> Dict:
        """Create a standard result dictionary"""
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'should_alert': is_empty and confidence > self.confidence_threshold,
            'method_scores': {},
            'stability': 0,
            'analysis_details': {'reason': reason}
        }
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(1.0, new_sensitivity))
        self.empty_threshold = 1.0 - self.sensitivity
    
    def reset_shelf_history(self, shelf_name: str = None):
        """Reset detection history for a shelf or all shelves"""
        if shelf_name:
            if shelf_name in self.detection_history:
                self.detection_history[shelf_name] = []
                self.alert_cooldown[shelf_name] = 0
        else:
            self.detection_history.clear()
            self.alert_cooldown.clear()
    
    def get_shelf_statistics(self, shelf_name: str) -> Dict:
        """Get statistics for a specific shelf"""
        if shelf_name not in self.detection_history:
            return {}
        
        history = self.detection_history[shelf_name]
        if not history:
            return {}
        
        empty_count = sum(1 for h in history if h['is_empty'])
        avg_confidence = np.mean([h['confidence'] for h in history])
        
        return {
            'total_detections': len(history),
            'empty_detections': empty_count,
            'empty_percentage': empty_count / len(history) * 100,
            'average_confidence': avg_confidence,
            'last_detection': history[-1]['timestamp'],
            'stability_score': len(history) / self.history_length
        }
