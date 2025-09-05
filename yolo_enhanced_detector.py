"""
YOLO-Enhanced Empty Shelf Detector with Advanced Visual Feedback
Uses YOLO-inspired detection with better accuracy and visual alerts
"""
import cv2
import numpy as np
import time
from typing import Dict, Tuple, List
import logging

class YOLOShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        
        # YOLO-inspired detection parameters
        self.confidence_threshold = 0.4
        self.nms_threshold = 0.5
        
        # Enhanced thresholds for better empty shelf detection
        self.detection_params = {
            'min_object_area': 500,        # Minimum area for object detection
            'color_variance_threshold': 800,  # Higher = more products detected
            'edge_density_threshold': 0.05,   # Minimum edge density for products
            'texture_complexity': 0.01,      # Texture analysis threshold
            'brightness_consistency': 15,     # Brightness variation threshold
            'contour_significance': 3        # Minimum significant contours
        }
        
        # Visual feedback system
        self.visual_states = {
            'CRITICALLY_EMPTY': {'color': (0, 0, 255), 'thickness': 6, 'confidence_min': 0.85},      # Bright red
            'MOSTLY_EMPTY': {'color': (0, 69, 255), 'thickness': 5, 'confidence_min': 0.70},        # Orange-red
            'PARTIALLY_EMPTY': {'color': (0, 165, 255), 'thickness': 4, 'confidence_min': 0.55},    # Orange
            'LOW_STOCK': {'color': (0, 255, 255), 'thickness': 3, 'confidence_min': 0.40},          # Yellow
            'WELL_STOCKED': {'color': (0, 255, 0), 'thickness': 3, 'confidence_min': 0.0},          # Green
            'UNCERTAIN': {'color': (128, 128, 128), 'thickness': 2, 'confidence_min': 0.0}          # Gray
        }
        
        # Alert system
        self.alert_levels = {
            'CRITICAL': {'sound': True, 'duration': 5000, 'priority': 1},
            'HIGH': {'sound': True, 'duration': 4000, 'priority': 2},
            'MEDIUM': {'sound': False, 'duration': 3000, 'priority': 3},
            'LOW': {'sound': False, 'duration': 2000, 'priority': 4}
        }
        
        # History tracking
        self.history_length = 10
        self.cooldown_time = 1.5
        
        print("🎯 YOLO-Enhanced Shelf Detector initialized with advanced visual feedback")
        
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Advanced YOLO-inspired analysis with comprehensive visual feedback
        """
        if timestamp is None:
            timestamp = time.time()
        
        if roi is None or roi.size == 0:
            return self._create_error_result("No image data", shelf_name)
        
        if roi.shape[0] < 50 or roi.shape[1] < 50:
            return self._create_error_result("Region too small for analysis", shelf_name)
        
        self.frame_count += 1
        
        # Initialize detection history
        if shelf_name not in self.detection_history:
            self.detection_history[shelf_name] = []
            self.alert_cooldown[shelf_name] = 0
        
        # Perform multi-stage YOLO-inspired analysis
        analysis_results = self._perform_yolo_analysis(roi)
        
        # Calculate advanced confidence scores
        confidence_data = self._calculate_yolo_confidence(analysis_results)
        
        # Determine visual state and alert level
        visual_state = self._determine_visual_state(confidence_data['empty_confidence'], 
                                                   confidence_data['is_empty'])
        alert_level = self._determine_alert_level(confidence_data['empty_confidence'], 
                                                 confidence_data['is_empty'])
        
        # Update detection history with rich data
        detection_record = {
            'timestamp': timestamp,
            'is_empty': confidence_data['is_empty'],
            'empty_confidence': confidence_data['empty_confidence'],
            'fullness_score': confidence_data['fullness_score'],
            'visual_state': visual_state,
            'alert_level': alert_level,
            'analysis': analysis_results,
            'frame_number': self.frame_count
        }
        
        self.detection_history[shelf_name].append(detection_record)
        
        # Maintain history size
        if len(self.detection_history[shelf_name]) > self.history_length:
            self.detection_history[shelf_name].pop(0)
        
        # Calculate stability and consistency
        stability_data = self._calculate_stability_metrics(shelf_name)
        
        # Determine if alert should be triggered
        should_alert = self._should_trigger_alert(shelf_name, timestamp, 
                                                 confidence_data, stability_data, alert_level)
        
        # Create comprehensive result
        return {
            'is_empty': confidence_data['is_empty'],
            'confidence': confidence_data['empty_confidence'],
            'fullness_score': confidence_data['fullness_score'],
            'should_alert': should_alert,
            'alert_level': alert_level,
            'visual_state': visual_state,
            'stability': stability_data['consistency_score'],
            'detection_strength': stability_data['detection_strength'],
            'details': analysis_results,
            'visual_feedback': self._get_visual_feedback_data(visual_state, alert_level),
            'method_scores': confidence_data['method_scores'],
            'frame_count': self.frame_count,
            'timestamp': timestamp,
            'trend': stability_data['trend']
        }
    
    def _perform_yolo_analysis(self, roi: np.ndarray) -> Dict:
        """
        YOLO-inspired multi-stage analysis
        """
        # Prepare different representations
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi.copy()
        
        # Stage 1: Object-like feature detection (YOLO-inspired)
        object_features = self._detect_object_features(roi, gray)
        
        # Stage 2: Advanced color analysis
        color_analysis = self._advanced_color_analysis(roi)
        
        # Stage 3: Texture and pattern analysis
        texture_analysis = self._texture_pattern_analysis(gray)
        
        # Stage 4: Spatial distribution analysis
        spatial_analysis = self._spatial_distribution_analysis(gray)
        
        # Stage 5: Edge and contour analysis
        structure_analysis = self._structure_analysis(gray)
        
        return {
            'object_features': object_features,
            'color_analysis': color_analysis,
            'texture_analysis': texture_analysis,
            'spatial_analysis': spatial_analysis,
            'structure_analysis': structure_analysis,
            'roi_shape': roi.shape
        }
    
    def _detect_object_features(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """
        Detect object-like features similar to YOLO detection
        """
        # Adaptive thresholding for object segmentation
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 11, 2)
        
        # Find contours (potential objects)
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter significant objects
        significant_objects = []
        total_object_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.detection_params['min_object_area']:
                # Calculate object properties
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
                significant_objects.append({
                    'area': area,
                    'bbox': (x, y, w, h),
                    'aspect_ratio': aspect_ratio,
                    'extent': extent
                })
                total_object_area += area
        
        roi_area = roi.shape[0] * roi.shape[1]
        coverage_ratio = total_object_area / roi_area if roi_area > 0 else 0
        
        # Calculate density more appropriately
        object_density = min(1.0, coverage_ratio * 3 + len(significant_objects) * 0.1)
        
        return {
            'object_count': len(significant_objects),
            'total_object_area': total_object_area,
            'coverage_ratio': coverage_ratio,
            'objects': significant_objects,
            'density_score': object_density
        }
    
    def _advanced_color_analysis(self, roi: np.ndarray) -> Dict:
        """
        Advanced color analysis for product detection
        """
        if len(roi.shape) == 3:
            # Convert to multiple color spaces
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Calculate color diversity
            color_variance_bgr = np.var(roi, axis=(0, 1))
            color_variance_hsv = np.var(hsv, axis=(0, 1))
            
            # Color histogram analysis
            hist_b = cv2.calcHist([roi], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([roi], [1], None, [32], [0, 256])
            hist_r = cv2.calcHist([roi], [2], None, [32], [0, 256])
            
            # Calculate color richness
            color_peaks = 0
            for hist in [hist_b, hist_g, hist_r]:
                peaks = len([i for i in range(1, 31) if hist[i] > hist[i-1] and hist[i] > hist[i+1]])
                color_peaks += peaks
            
            color_diversity = np.mean(color_variance_bgr) + np.mean(color_variance_hsv)
            
        else:
            color_diversity = np.var(roi)
            color_peaks = 0
        
        return {
            'color_diversity': color_diversity,
            'color_peaks': color_peaks,
            'richness_score': color_diversity / 1000.0 + color_peaks / 10.0
        }
    
    def _texture_pattern_analysis(self, gray: np.ndarray) -> Dict:
        """
        Analyze texture patterns that indicate product presence
        """
        # Local Binary Pattern approximation
        kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]], dtype=np.float32)
        filtered = cv2.filter2D(gray, -1, kernel)
        texture_response = np.var(filtered)
        
        # Gradient analysis
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        texture_strength = np.mean(gradient_magnitude)
        
        # Pattern complexity
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        pattern_complexity = np.var(laplacian)
        
        return {
            'texture_response': texture_response,
            'texture_strength': texture_strength,
            'pattern_complexity': pattern_complexity,
            'combined_texture_score': (texture_response / 1000.0 + 
                                     texture_strength / 100.0 + 
                                     pattern_complexity / 1000.0) / 3.0
        }
    
    def _spatial_distribution_analysis(self, gray: np.ndarray) -> Dict:
        """
        Analyze spatial distribution of features
        """
        # Divide into grid and analyze each section
        h, w = gray.shape
        grid_size = 4
        section_h, section_w = h // grid_size, w // grid_size
        
        section_variances = []
        section_means = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                y1, y2 = i * section_h, min((i + 1) * section_h, h)
                x1, x2 = j * section_w, min((j + 1) * section_w, w)
                
                section = gray[y1:y2, x1:x2]
                if section.size > 0:
                    section_variances.append(np.var(section))
                    section_means.append(np.mean(section))
        
        spatial_uniformity = np.std(section_variances) if section_variances else 0
        brightness_distribution = np.std(section_means) if section_means else 0
        
        return {
            'spatial_uniformity': spatial_uniformity,
            'brightness_distribution': brightness_distribution,
            'distribution_score': (spatial_uniformity + brightness_distribution) / 2.0
        }
    
    def _structure_analysis(self, gray: np.ndarray) -> Dict:
        """
        Analyze structural elements
        """
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Line detection
        try:
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            line_count = len(lines) if lines is not None else 0
        except:
            line_count = 0
        
        # Corner detection
        try:
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, 
                                             minDistance=10)
            corner_count = len(corners) if corners is not None else 0
        except:
            corner_count = 0
        
        return {
            'edge_density': edge_density,
            'line_count': line_count,
            'corner_count': corner_count,
            'structure_score': edge_density * 10 + line_count / 10.0 + corner_count / 10.0
        }
    
    def _calculate_yolo_confidence(self, analysis: Dict) -> Dict:
        """
        Calculate confidence scores using YOLO-inspired weighting
        """
        # Extract key metrics
        object_density = analysis['object_features']['density_score']
        color_richness = analysis['color_analysis']['richness_score']
        texture_score = analysis['texture_analysis']['combined_texture_score']
        spatial_score = analysis['spatial_analysis']['distribution_score']
        structure_score = analysis['structure_analysis']['structure_score']
        
        # YOLO-inspired weighted scoring with better empty detection
        weights = {
            'objects': 0.4,       # Primary indicator - increased weight
            'color': 0.2,         # Color diversity
            'texture': 0.2,       # Surface patterns
            'spatial': 0.1,       # Distribution
            'structure': 0.1      # Edges and lines
        }
        
        # Calculate fullness score (0 = empty, 1 = full) with better scaling
        fullness_score = (
            weights['objects'] * min(1.0, object_density) +
            weights['color'] * min(1.0, color_richness / 2.0) +
            weights['texture'] * min(1.0, texture_score * 2.0) +
            weights['spatial'] * min(1.0, spatial_score / 25.0) +
            weights['structure'] * min(1.0, structure_score / 5.0)
        )
        
        # Apply sensitivity adjustment (more conservative)
        adjusted_fullness = fullness_score * (1.5 - self.sensitivity * 0.5)
        
        # Determine empty status and confidence with better threshold
        empty_threshold = 0.3  # Lower threshold for better empty detection
        is_empty = adjusted_fullness < empty_threshold
        
        if is_empty:
            empty_confidence = (empty_threshold - adjusted_fullness) / empty_threshold
        else:
            empty_confidence = (adjusted_fullness - empty_threshold) / (1.0 - empty_threshold)
        
        # Ensure confidence is in valid range
        empty_confidence = max(0.0, min(1.0, empty_confidence))
        
        return {
            'fullness_score': adjusted_fullness,
            'is_empty': is_empty,
            'empty_confidence': empty_confidence,
            'method_scores': {
                'object_detection': min(1.0, object_density),
                'color_analysis': min(1.0, color_richness / 2.0),
                'texture_analysis': min(1.0, texture_score * 2.0),
                'spatial_analysis': min(1.0, spatial_score / 25.0),
                'structure_analysis': min(1.0, structure_score / 5.0)
            }
        }
    
    def _determine_visual_state(self, confidence: float, is_empty: bool) -> str:
        """
        Determine visual state based on confidence
        """
        if not is_empty:
            return 'WELL_STOCKED'
        
        if confidence >= 0.85:
            return 'CRITICALLY_EMPTY'
        elif confidence >= 0.70:
            return 'MOSTLY_EMPTY'
        elif confidence >= 0.55:
            return 'PARTIALLY_EMPTY'
        elif confidence >= 0.40:
            return 'LOW_STOCK'
        else:
            return 'UNCERTAIN'
    
    def _determine_alert_level(self, confidence: float, is_empty: bool) -> str:
        """
        Determine alert level
        """
        if not is_empty:
            return 'NONE'
        
        if confidence >= 0.85:
            return 'CRITICAL'
        elif confidence >= 0.70:
            return 'HIGH'
        elif confidence >= 0.55:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_stability_metrics(self, shelf_name: str) -> Dict:
        """
        Calculate stability and trend metrics
        """
        history = self.detection_history[shelf_name]
        if len(history) < 3:
            return {
                'consistency_score': len(history),
                'detection_strength': 0.5,
                'trend': 'UNKNOWN'
            }
        
        # Calculate consistency
        recent_states = [h['is_empty'] for h in history[-5:]]
        consistent_detections = sum(1 for state in recent_states if state == recent_states[-1])
        consistency_score = min(5, consistent_detections)
        
        # Calculate detection strength
        recent_confidences = [h['empty_confidence'] for h in history[-3:]]
        detection_strength = np.mean(recent_confidences)
        
        # Calculate trend
        if len(history) >= 5:
            old_avg = np.mean([h['fullness_score'] for h in history[-5:-2]])
            new_avg = np.mean([h['fullness_score'] for h in history[-3:]])
            
            if new_avg > old_avg + 0.1:
                trend = 'IMPROVING'
            elif new_avg < old_avg - 0.1:
                trend = 'DECLINING'
            else:
                trend = 'STABLE'
        else:
            trend = 'UNKNOWN'
        
        return {
            'consistency_score': consistency_score,
            'detection_strength': detection_strength,
            'trend': trend
        }
    
    def _should_trigger_alert(self, shelf_name: str, timestamp: float, 
                             confidence_data: Dict, stability_data: Dict, alert_level: str) -> bool:
        """
        Enhanced alert triggering logic
        """
        if not confidence_data['is_empty'] or alert_level == 'NONE':
            return False
        
        # Check minimum confidence
        if confidence_data['empty_confidence'] < 0.5:
            return False
        
        # Check stability requirement
        if stability_data['consistency_score'] < 2:
            return False
        
        # Check cooldown
        if timestamp - self.alert_cooldown[shelf_name] < self.cooldown_time:
            return False
        
        # Update cooldown
        self.alert_cooldown[shelf_name] = timestamp
        return True
    
    def _get_visual_feedback_data(self, visual_state: str, alert_level: str) -> Dict:
        """
        Get visual feedback configuration
        """
        state_config = self.visual_states.get(visual_state, self.visual_states['UNCERTAIN'])
        alert_config = self.alert_levels.get(alert_level, self.alert_levels['LOW'])
        
        return {
            'color': state_config['color'],
            'thickness': state_config['thickness'],
            'should_pulse': alert_level in ['CRITICAL', 'HIGH'],
            'alert_duration': alert_config['duration'],
            'play_sound': alert_config['sound'],
            'priority': alert_config['priority']
        }
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(1.0, new_sensitivity))
        print(f"🎯 Detection sensitivity updated to: {self.sensitivity:.2f}")
    
    def get_detection_summary(self, shelf_name: str) -> Dict:
        """
        Get comprehensive detection summary for a shelf
        """
        if shelf_name not in self.detection_history:
            return {'status': 'No detection history'}
        
        history = self.detection_history[shelf_name]
        recent = history[-1] if history else None
        
        if not recent:
            return {'status': 'No recent detection'}
        
        return {
            'current_state': recent['visual_state'],
            'confidence': recent['empty_confidence'],
            'alert_level': recent['alert_level'],
            'trend': self._calculate_stability_metrics(shelf_name)['trend'],
            'detection_count': len(history),
            'last_update': recent['timestamp']
        }
    
    def _create_error_result(self, error_message: str, shelf_name: str) -> Dict:
        """Create error result"""
        return {
            'is_empty': True,
            'confidence': 1.0,
            'fullness_score': 0.0,
            'should_alert': False,
            'alert_level': 'CRITICAL',
            'visual_state': 'CRITICALLY_EMPTY',
            'stability': 0,
            'detection_strength': 0.0,
            'details': {'error': error_message},
            'visual_feedback': self._get_visual_feedback_data('CRITICALLY_EMPTY', 'CRITICAL'),
            'method_scores': {method: 0.0 for method in ['object_detection', 'color_analysis', 
                                                        'texture_analysis', 'spatial_analysis', 'structure_analysis']},
            'frame_count': self.frame_count,
            'timestamp': time.time(),
            'trend': 'UNKNOWN'
        }
