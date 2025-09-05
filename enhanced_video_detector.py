"""
Enhanced Empty Shelf Detector - Improved for Video Analysis
Superior empty shelf detection specifically tuned for supermarket videos
"""
import os

# Fix OpenMP library conflict (must be before other imports)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
import time
from typing import Dict, Tuple, List

class EnhancedVideoShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        
        # Aggressively tuned parameters for supermarket video empty shelf detection
        self.detection_params = {
            'min_object_area': 300,           # Much lower for video quality
            'max_empty_variance': 150,        # Very strict for empty detection
            'min_color_diversity': 600,       # Reduced for compressed video
            'min_texture_strength': 6,        # Lower for video artifacts
            'edge_density_threshold': 0.015,  # Very sensitive edge detection
            'uniformity_threshold': 0.65,     # More aggressive empty detection
            'contrast_threshold': 15,         # Lower for video compression
            'supermarket_mode': True,         # Always enabled
            'video_compression_factor': 0.75, # Strong compensation
            'lighting_variance_threshold': 100, # Strict lighting check
            'shelf_background_tolerance': 0.08, # Very tight tolerance
            'empty_confidence_boost': 0.25,   # Strong boost for empty detection
            'aggressive_empty_detection': True, # New aggressive mode
            'multi_threshold_analysis': True,  # Multiple threshold analysis
            'temporal_consistency_weight': 0.3 # Consider detection history
        }
        
        # Enhanced visual states with better empty detection feedback
        self.visual_states = {
            'CRITICALLY_EMPTY': {'color': (0, 0, 255), 'thickness': 8, 'confidence_min': 0.80},
            'MOSTLY_EMPTY': {'color': (0, 69, 255), 'thickness': 6, 'confidence_min': 0.65},
            'PARTIALLY_EMPTY': {'color': (0, 165, 255), 'thickness': 5, 'confidence_min': 0.50},
            'LOW_STOCK': {'color': (0, 255, 255), 'thickness': 4, 'confidence_min': 0.35},
            'WELL_STOCKED': {'color': (0, 255, 0), 'thickness': 3, 'confidence_min': 0.0},
            'UNCERTAIN': {'color': (128, 128, 128), 'thickness': 2, 'confidence_min': 0.0}
        }
        
        # History tracking for temporal consistency
        self.history_length = 8
        self.cooldown_time = 0.8
        
        print("🎯 Enhanced Video Shelf Detector initialized - Aggressive empty detection mode")
    
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Enhanced analysis with aggressive empty shelf detection for video
        """
        if timestamp is None:
            timestamp = time.time()
        
        if roi is None or roi.size == 0:
            return self._create_error_result("No image data", shelf_name)
        
        if roi.shape[0] < 30 or roi.shape[1] < 30:
            return self._create_error_result("Region too small for analysis", shelf_name)
        
        self.frame_count += 1
        
        # Initialize detection history
        if shelf_name not in self.detection_history:
            self.detection_history[shelf_name] = []
            self.alert_cooldown[shelf_name] = 0
        
        # Perform enhanced analysis with multiple methods
        analysis_results = self._perform_enhanced_video_analysis(roi)
        
        # Calculate confidence with aggressive empty detection
        confidence_data = self._calculate_enhanced_confidence(analysis_results, shelf_name)
        
        # Determine visual state and alert level
        visual_state = self._determine_visual_state(confidence_data['empty_confidence'], 
                                                   confidence_data['is_empty'])
        alert_level = self._determine_alert_level(confidence_data['empty_confidence'], 
                                                 confidence_data['is_empty'])
        
        # Update detection history
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
        
        # Determine if alert should be triggered
        should_alert = self._should_trigger_alert(shelf_name, confidence_data, timestamp)
        
        return {
            'is_empty': confidence_data['is_empty'],
            'confidence': confidence_data['empty_confidence'],
            'fullness_score': confidence_data['fullness_score'],
            'visual_state': visual_state,
            'alert_level': alert_level,
            'should_alert': should_alert,
            'method_scores': confidence_data['method_scores'],
            'analysis_details': analysis_results,
            'trend': self._calculate_trend(shelf_name),
            'yolo_products': []  # Compatibility with YOLO interface
        }
    
    def _perform_enhanced_video_analysis(self, roi: np.ndarray) -> Dict:
        """
        Enhanced analysis specifically tuned for video with aggressive empty detection
        """
        # Convert to grayscale
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Multiple analysis methods with video optimization
        uniformity_analysis = self._analyze_enhanced_uniformity(roi, gray)
        object_analysis = self._detect_enhanced_objects(roi, gray)
        color_analysis = self._enhanced_color_analysis(roi)
        texture_analysis = self._analyze_enhanced_texture(gray)
        structure_analysis = self._analyze_enhanced_structure(gray)
        
        # New: Multi-threshold analysis for better empty detection
        threshold_analysis = self._multi_threshold_analysis(gray)
        
        # New: Spatial analysis for empty regions
        spatial_analysis = self._spatial_empty_analysis(gray)
        
        return {
            'uniformity': uniformity_analysis,
            'objects': object_analysis,
            'color': color_analysis,
            'texture': texture_analysis,
            'structure': structure_analysis,
            'threshold': threshold_analysis,
            'spatial': spatial_analysis,
            'roi_shape': roi.shape
        }
    
    def _analyze_enhanced_uniformity(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """Enhanced uniformity analysis for aggressive empty detection"""
        # Global variance
        total_variance = np.var(gray)
        
        # Local variance analysis with smaller patches for better sensitivity
        h, w = gray.shape
        patch_size = min(30, h//6, w//6)  # Smaller patches
        local_variances = []
        
        if patch_size > 0:
            for y in range(0, h - patch_size, patch_size//3):  # More overlap
                for x in range(0, w - patch_size, patch_size//3):
                    patch = gray[y:y+patch_size, x:x+patch_size]
                    local_variances.append(np.var(patch))
        
        variance_std = np.std(local_variances) if local_variances else 0
        mean_local_variance = np.mean(local_variances) if local_variances else 0
        
        # Enhanced histogram analysis
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])  # Fewer bins for video
        hist_normalized = hist / np.sum(hist)
        hist_entropy = -np.sum(hist_normalized * np.log(hist_normalized + 1e-7))
        
        # More aggressive uniformity scoring
        uniformity_score = 1.0 / (1.0 + variance_std * 0.5 + mean_local_variance/50.0)
        
        # Check for dominant color (empty shelf characteristic)
        dominant_color_ratio = np.max(hist_normalized)
        
        return {
            'total_variance': total_variance,
            'local_variance_std': variance_std,
            'mean_local_variance': mean_local_variance,
            'histogram_entropy': hist_entropy,
            'uniformity_score': uniformity_score,
            'dominant_color_ratio': dominant_color_ratio,
            'is_uniform': uniformity_score > self.detection_params['uniformity_threshold']
        }
    
    def _detect_enhanced_objects(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """Enhanced object detection with multiple thresholding approaches"""
        # Multiple thresholding methods for better object detection
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 11, 2)
        _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, simple_thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Combine thresholds for more robust detection
        combined_thresh = cv2.bitwise_and(adaptive_thresh, otsu_thresh)
        
        # Find contours
        contours, _ = cv2.findContours(combined_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter meaningful objects with lower thresholds for video
        meaningful_objects = []
        total_meaningful_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.detection_params['min_object_area']:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
                object_region = gray[y:y+h, x:x+w]
                contrast = np.max(object_region) - np.min(object_region) if object_region.size > 0 else 0
                
                # More lenient criteria for video quality
                if (contrast > self.detection_params['contrast_threshold'] and 
                    0.05 < aspect_ratio < 20 and extent > 0.2):
                    meaningful_objects.append({
                        'area': area,
                        'bbox': (x, y, w, h),
                        'aspect_ratio': aspect_ratio,
                        'extent': extent,
                        'contrast': contrast
                    })
                    total_meaningful_area += area
        
        # Calculate edge density with enhanced edge detection
        edges = cv2.Canny(gray, 30, 100)  # Lower thresholds for video
        edge_pixels = np.count_nonzero(edges)
        roi_area = roi.shape[0] * roi.shape[1]
        edge_density = edge_pixels / roi_area if roi_area > 0 else 0
        
        coverage_ratio = total_meaningful_area / roi_area if roi_area > 0 else 0
        
        # More aggressive object density calculation
        object_density = min(1.0, len(meaningful_objects) * 0.15 + coverage_ratio * 1.5)
        
        return {
            'meaningful_object_count': len(meaningful_objects),
            'total_meaningful_area': total_meaningful_area,
            'coverage_ratio': coverage_ratio,
            'objects': meaningful_objects,
            'object_density': object_density,
            'edge_density': edge_density
        }
    
    def _multi_threshold_analysis(self, gray: np.ndarray) -> Dict:
        """Multi-threshold analysis for robust empty detection"""
        thresholds = []
        
        # Different threshold methods
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, triangle = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
        
        # Manual thresholds for different lighting conditions
        manual_thresholds = [100, 120, 140, 160, 180]
        
        consistent_empty_count = 0
        threshold_scores = []
        
        for thresh_val in manual_thresholds:
            _, manual_thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
            
            # Count white pixels (potential empty areas)
            white_ratio = np.sum(manual_thresh == 255) / manual_thresh.size
            
            # Check uniformity of thresholded image
            if white_ratio > 0.7:  # Mostly white = likely empty
                consistent_empty_count += 1
            
            threshold_scores.append(white_ratio)
        
        # Consensus scoring
        avg_white_ratio = np.mean(threshold_scores)
        consistency_score = consistent_empty_count / len(manual_thresholds)
        
        return {
            'consistent_empty_count': consistent_empty_count,
            'avg_white_ratio': avg_white_ratio,
            'consistency_score': consistency_score,
            'threshold_scores': threshold_scores,
            'suggests_empty': consistency_score > 0.6 and avg_white_ratio > 0.6
        }
    
    def _spatial_empty_analysis(self, gray: np.ndarray) -> Dict:
        """Spatial analysis to identify empty regions"""
        h, w = gray.shape
        
        # Divide into grid for spatial analysis
        grid_size = 4
        cell_h, cell_w = h // grid_size, w // grid_size
        
        empty_cells = 0
        cell_variances = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                y1, y2 = i * cell_h, (i + 1) * cell_h
                x1, x2 = j * cell_w, (j + 1) * cell_w
                
                if y2 <= h and x2 <= w:
                    cell = gray[y1:y2, x1:x2]
                    cell_var = np.var(cell)
                    cell_variances.append(cell_var)
                    
                    # Check if cell appears empty (low variance + high mean)
                    if cell_var < 100 and np.mean(cell) > 150:
                        empty_cells += 1
        
        total_cells = grid_size * grid_size
        empty_ratio = empty_cells / total_cells if total_cells > 0 else 0
        
        return {
            'empty_cells': empty_cells,
            'total_cells': total_cells,
            'empty_ratio': empty_ratio,
            'cell_variances': cell_variances,
            'spatial_suggests_empty': empty_ratio > 0.7
        }
    
    def _enhanced_color_analysis(self, roi: np.ndarray) -> Dict:
        """Enhanced color analysis for video"""
        if len(roi.shape) == 3:
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # More sensitive color variance calculation
            color_variance_bgr = np.var(roi, axis=(0, 1))
            color_variance_hsv = np.var(hsv, axis=(0, 1))
            total_color_variance = np.sum(color_variance_bgr) + np.sum(color_variance_hsv)
            
            # Reduced histogram bins for video compression
            hist_b = cv2.calcHist([roi], [0], None, [16], [0, 256])
            hist_g = cv2.calcHist([roi], [1], None, [16], [0, 256])
            hist_r = cv2.calcHist([roi], [2], None, [16], [0, 256])
            
            # More aggressive color richness calculation
            color_richness = (np.count_nonzero(hist_b > hist_b.max() * 0.05) +
                            np.count_nonzero(hist_g > hist_g.max() * 0.05) +
                            np.count_nonzero(hist_r > hist_r.max() * 0.05)) / 48.0
        else:
            total_color_variance = np.var(roi)
            color_richness = 0.1
        
        # More aggressive diversity threshold for empty detection
        has_diverse_colors = total_color_variance > self.detection_params['min_color_diversity']
        
        return {
            'total_color_variance': total_color_variance,
            'color_richness': min(1.0, color_richness),
            'has_diverse_colors': has_diverse_colors
        }
    
    def _analyze_enhanced_texture(self, gray: np.ndarray) -> Dict:
        """Enhanced texture analysis for video"""
        # Multiple texture measures
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Sobel gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobelx**2 + sobely**2)
        sobel_mean = np.mean(sobel_magnitude)
        
        # Local Binary Pattern approximation
        lbp_approx = cv2.filter2D(gray, cv2.CV_64F, np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]))
        lbp_var = np.var(lbp_approx)
        
        # Enhanced texture scoring
        texture_score = min(1.0, (laplacian_var + sobel_mean * 8 + lbp_var * 0.1) / 800.0)
        has_texture = texture_score > (self.detection_params['min_texture_strength'] / 100.0)
        
        return {
            'laplacian_variance': laplacian_var,
            'sobel_magnitude_mean': sobel_mean,
            'lbp_variance': lbp_var,
            'texture_score': texture_score,
            'has_texture': has_texture
        }
    
    def _analyze_enhanced_structure(self, gray: np.ndarray) -> Dict:
        """Enhanced structural analysis"""
        # Corner detection with lower quality threshold
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.005, minDistance=5)
        corner_count = len(corners) if corners is not None else 0
        
        # Line detection with more sensitive parameters
        edges = cv2.Canny(gray, 20, 80)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=15)
        line_count = len(lines) if lines is not None else 0
        
        # More conservative structure scoring for empty detection
        structure_score = corner_count + line_count * 1.5
        has_structure = structure_score > 15  # Lower threshold
        
        return {
            'corner_count': corner_count,
            'line_count': line_count,
            'structure_score': structure_score,
            'has_structure': has_structure
        }
    
    def _calculate_enhanced_confidence(self, analysis: Dict, shelf_name: str) -> Dict:
        """
        Enhanced confidence calculation with aggressive empty detection
        """
        uniformity = analysis['uniformity']
        objects = analysis['objects']
        color = analysis['color']
        texture = analysis['texture']
        structure = analysis['structure']
        threshold = analysis['threshold']
        spatial = analysis['spatial']
        
        # Traditional empty indicators
        is_uniform = uniformity['is_uniform']
        has_few_objects = objects['meaningful_object_count'] <= 1
        low_color_diversity = not color['has_diverse_colors']
        low_texture = not texture['has_texture']
        minimal_structure = not structure['has_structure']
        
        # Enhanced empty indicators
        threshold_suggests_empty = threshold['suggests_empty']
        spatial_suggests_empty = spatial['spatial_suggests_empty']
        dominant_color = uniformity['dominant_color_ratio'] > 0.4
        very_low_edge_density = objects['edge_density'] < self.detection_params['edge_density_threshold']
        
        # Aggressive empty indicators list
        all_empty_indicators = [
            is_uniform,
            has_few_objects,
            low_color_diversity,
            low_texture,
            minimal_structure,
            threshold_suggests_empty,
            spatial_suggests_empty,
            dominant_color,
            very_low_edge_density
        ]
        
        empty_indicator_count = sum(all_empty_indicators)
        
        # Temporal consistency check
        temporal_boost = 0.0
        if (shelf_name in self.detection_history and 
            len(self.detection_history[shelf_name]) >= 3):
            recent_empty_count = sum(1 for r in self.detection_history[shelf_name][-3:] 
                                   if r.get('is_empty', False))
            temporal_boost = (recent_empty_count / 3) * self.detection_params['temporal_consistency_weight']
        
        # Aggressive confidence calculation
        if empty_indicator_count >= 6:  # Very strong evidence
            empty_confidence = 0.90 + min(0.10, (empty_indicator_count - 6) * 0.02)
            is_empty = True
        elif empty_indicator_count >= 4:  # Strong evidence
            empty_confidence = 0.75 + (empty_indicator_count - 4) * 0.05
            is_empty = True
        elif empty_indicator_count >= 3:  # Moderate evidence
            empty_confidence = 0.55 + (empty_indicator_count - 3) * 0.1
            is_empty = True
        elif empty_indicator_count >= 2:  # Some evidence
            empty_confidence = 0.35 + (empty_indicator_count - 2) * 0.1
            is_empty = empty_indicator_count >= 3 or temporal_boost > 0.2
        else:  # Likely has products
            is_empty = False
            fullness_score = (
                objects['object_density'] * 0.4 +
                color['color_richness'] * 0.3 +
                texture['texture_score'] * 0.2 +
                structure['structure_score'] / 10.0 * 0.1
            ) * self.detection_params['video_compression_factor']
            empty_confidence = max(0.05, 1.0 - fullness_score)
        
        # Apply aggressive empty detection boost
        if is_empty:
            empty_confidence += self.detection_params['empty_confidence_boost']
            empty_confidence += temporal_boost
            empty_confidence = min(1.0, empty_confidence)
        
        # Apply sensitivity
        if is_empty:
            sensitivity_boost = 1.0 + self.sensitivity * 0.15
            empty_confidence = min(1.0, empty_confidence * sensitivity_boost)
        else:
            empty_confidence = max(0.0, empty_confidence * (2.0 - self.sensitivity))
        
        return {
            'is_empty': is_empty,
            'empty_confidence': empty_confidence,
            'fullness_score': 1.0 - empty_confidence if is_empty else empty_confidence,
            'method_scores': {
                'uniformity_analysis': uniformity['uniformity_score'],
                'object_detection': objects['object_density'],
                'color_analysis': color['color_richness'],
                'texture_analysis': texture['texture_score'],
                'structure_analysis': min(1.0, structure['structure_score'] / 10.0),
                'threshold_analysis': threshold['consistency_score'],
                'spatial_analysis': spatial['empty_ratio']
            },
            'empty_indicators': empty_indicator_count,
            'temporal_boost': temporal_boost
        }
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(0.9, new_sensitivity))
        print(f"🎯 Enhanced detection sensitivity updated to: {self.sensitivity:.2f}")
    
    def _determine_visual_state(self, confidence: float, is_empty: bool) -> str:
        """Determine visual state based on confidence"""
        if not is_empty:
            return 'WELL_STOCKED'
        
        if confidence >= 0.80:
            return 'CRITICALLY_EMPTY'
        elif confidence >= 0.65:
            return 'MOSTLY_EMPTY'
        elif confidence >= 0.50:
            return 'PARTIALLY_EMPTY'
        elif confidence >= 0.35:
            return 'LOW_STOCK'
        else:
            return 'UNCERTAIN'
    
    def _determine_alert_level(self, confidence: float, is_empty: bool) -> str:
        """Determine alert level"""
        if not is_empty:
            return 'LOW'
        
        if confidence >= 0.80:
            return 'CRITICAL'
        elif confidence >= 0.65:
            return 'HIGH'
        elif confidence >= 0.50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _should_trigger_alert(self, shelf_name: str, confidence_data: Dict, timestamp: float) -> bool:
        """Determine if alert should be triggered"""
        if not confidence_data['is_empty']:
            return False
        
        if timestamp - self.alert_cooldown.get(shelf_name, 0) < self.cooldown_time:
            return False
        
        confidence = confidence_data['empty_confidence']
        # Lower threshold for more responsive alerts
        if confidence >= 0.55:  
            self.alert_cooldown[shelf_name] = timestamp
            return True
        
        return False
    
    def _calculate_trend(self, shelf_name: str) -> str:
        """Calculate trend based on history"""
        if shelf_name not in self.detection_history or len(self.detection_history[shelf_name]) < 3:
            return 'UNKNOWN'
        
        recent_records = self.detection_history[shelf_name][-5:]
        confidences = [r['empty_confidence'] for r in recent_records]
        
        if len(confidences) >= 3:
            trend_slope = np.polyfit(range(len(confidences)), confidences, 1)[0]
            if trend_slope > 0.05:
                return 'EMPTYING'
            elif trend_slope < -0.05:
                return 'FILLING'
            else:
                return 'STABLE'
        
        return 'UNKNOWN'
    
    def _create_error_result(self, error_message: str, shelf_name: str) -> Dict:
        """Create error result"""
        return {
            'is_empty': False,
            'confidence': 0.0,
            'fullness_score': 0.0,
            'visual_state': 'UNCERTAIN',
            'alert_level': 'LOW',
            'should_alert': False,
            'method_scores': {},
            'analysis_details': {},
            'trend': 'UNKNOWN',
            'error': error_message,
            'yolo_products': []
        }
