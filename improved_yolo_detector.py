"""
Improved YOLO-Enhanced Empty Shelf Detector with Better Empty Detection
Addresses the issue where empty shelves are incorrectly detected as stocked
"""
import os

# Fix OpenMP library conflict (must be before other imports)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
import time
from typing import Dict, Tuple, List
import logging

class ImprovedYOLODetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        
        # Enhanced detection parameters for supermarket videos with better empty shelf recognition
        self.detection_params = {
            'min_object_area': 600,           # Adjusted for supermarket video quality
            'max_empty_variance': 300,        # Stricter variance for empty areas
            'min_color_diversity': 1200,      # Adjusted color diversity for products
            'min_texture_strength': 12,       # Adjusted texture for supermarket lighting
            'edge_density_threshold': 0.025,  # Optimized edge density for video format
            'uniformity_threshold': 0.80,     # Fine-tuned uniformity for recorded video
            'contrast_threshold': 25,         # Adjusted contrast for video compression
            'supermarket_mode': True,         # Special handling for supermarket videos
            'video_compression_factor': 0.85, # Compensation for video compression
            'lighting_variance_threshold': 150, # Account for supermarket lighting
            'shelf_background_tolerance': 0.15 # Tolerance for shelf background patterns
        }
        
        # Visual feedback system
        self.visual_states = {
            'CRITICALLY_EMPTY': {'color': (0, 0, 255), 'thickness': 6, 'confidence_min': 0.85},
            'MOSTLY_EMPTY': {'color': (0, 69, 255), 'thickness': 5, 'confidence_min': 0.70},
            'PARTIALLY_EMPTY': {'color': (0, 165, 255), 'thickness': 4, 'confidence_min': 0.55},
            'LOW_STOCK': {'color': (0, 255, 255), 'thickness': 3, 'confidence_min': 0.40},
            'WELL_STOCKED': {'color': (0, 255, 0), 'thickness': 3, 'confidence_min': 0.0},
            'UNCERTAIN': {'color': (128, 128, 128), 'thickness': 2, 'confidence_min': 0.0}
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
        
        print("🎯 Improved YOLO Shelf Detector initialized with better empty detection")
        
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Advanced analysis with improved empty shelf detection
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
        
        # Perform improved analysis
        analysis_results = self._perform_improved_analysis(roi)
        
        # Calculate confidence with better empty detection
        confidence_data = self._calculate_improved_confidence(analysis_results)
        
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
        
        # Calculate stability
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
    
    def _perform_improved_analysis(self, roi: np.ndarray) -> Dict:
        """
        Improved analysis with better empty shelf detection
        """
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi.copy()
        
        # 1. Uniformity analysis (key for empty detection)
        uniformity_analysis = self._analyze_uniformity(roi, gray)
        
        # 2. Sophisticated object detection
        object_analysis = self._detect_meaningful_objects(roi, gray)
        
        # 3. Advanced color analysis
        color_analysis = self._advanced_color_analysis(roi)
        
        # 4. Texture analysis
        texture_analysis = self._analyze_texture_patterns(gray)
        
        # 5. Structure analysis
        structure_analysis = self._analyze_structure(gray)
        
        return {
            'uniformity': uniformity_analysis,
            'objects': object_analysis,
            'color': color_analysis,
            'texture': texture_analysis,
            'structure': structure_analysis,
            'roi_shape': roi.shape
        }
    
    def _analyze_uniformity(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """
        Analyze uniformity - key indicator of empty shelves
        """
        # Calculate variance across the entire region
        total_variance = np.var(gray)
        
        # Calculate local variance in patches
        h, w = gray.shape
        patch_size = min(50, h//4, w//4)
        local_variances = []
        
        for y in range(0, h - patch_size, patch_size//2):
            for x in range(0, w - patch_size, patch_size//2):
                patch = gray[y:y+patch_size, x:x+patch_size]
                local_variances.append(np.var(patch))
        
        # Calculate uniformity metrics
        variance_std = np.std(local_variances) if local_variances else 0
        mean_local_variance = np.mean(local_variances) if local_variances else 0
        
        # Calculate histogram uniformity
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist / np.sum(hist)
        hist_entropy = -np.sum(hist_normalized * np.log(hist_normalized + 1e-7))
        
        # Uniformity score (higher = more uniform = more likely empty)
        uniformity_score = 1.0 / (1.0 + variance_std + mean_local_variance/100.0)
        
        return {
            'total_variance': total_variance,
            'local_variance_std': variance_std,
            'mean_local_variance': mean_local_variance,
            'histogram_entropy': hist_entropy,
            'uniformity_score': uniformity_score,
            'is_uniform': uniformity_score > self.detection_params['uniformity_threshold']
        }
    
    def _detect_meaningful_objects(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """
        Detect meaningful objects that indicate products
        """
        # Use multiple thresholding approaches
        # 1. Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 15, 3)
        
        # 2. Otsu's thresholding
        _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Combine thresholds
        combined_thresh = cv2.bitwise_and(adaptive_thresh, otsu_thresh)
        
        # Find contours
        contours, _ = cv2.findContours(combined_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter meaningful objects
        meaningful_objects = []
        total_meaningful_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.detection_params['min_object_area']:
                # Additional checks for meaningful objects
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
                # Check if object has sufficient contrast
                object_region = gray[y:y+h, x:x+w]
                contrast = np.max(object_region) - np.min(object_region)
                
                if (contrast > self.detection_params['contrast_threshold'] and 
                    0.1 < aspect_ratio < 10 and extent > 0.3):
                    meaningful_objects.append({
                        'area': area,
                        'bbox': (x, y, w, h),
                        'aspect_ratio': aspect_ratio,
                        'extent': extent,
                        'contrast': contrast
                    })
                    total_meaningful_area += area
        
        roi_area = roi.shape[0] * roi.shape[1]
        coverage_ratio = total_meaningful_area / roi_area if roi_area > 0 else 0
        
        # Calculate edge density for empty shelf detection
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.count_nonzero(edges)
        edge_density = edge_pixels / roi_area if roi_area > 0 else 0
        
        return {
            'meaningful_object_count': len(meaningful_objects),
            'total_meaningful_area': total_meaningful_area,
            'coverage_ratio': coverage_ratio,
            'objects': meaningful_objects,
            'object_density': min(1.0, len(meaningful_objects) * 0.2 + coverage_ratio * 2),
            'edge_density': edge_density
        }
    
    def _advanced_color_analysis(self, roi: np.ndarray) -> Dict:
        """
        Advanced color analysis for product detection
        """
        if len(roi.shape) == 3:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Calculate color diversity
            color_variance_bgr = np.var(roi, axis=(0, 1))
            color_variance_hsv = np.var(hsv, axis=(0, 1))
            total_color_variance = np.sum(color_variance_bgr) + np.sum(color_variance_hsv)
            
            # Color histogram analysis
            hist_h = cv2.calcHist([hsv], [0], None, [32], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [32], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [32], [0, 256])
            
            # Count significant color peaks
            color_peaks = 0
            for hist in [hist_h, hist_s, hist_v]:
                hist_flat = hist.flatten()
                # Manual smoothing instead of GaussianBlur
                smoothed = np.convolve(hist_flat, np.ones(3)/3, mode='same')
                peaks = len([i for i in range(2, len(smoothed)-2) 
                           if smoothed[i] > smoothed[i-1] and 
                              smoothed[i] > smoothed[i+1] and 
                              smoothed[i] > np.mean(smoothed) * 1.5])
                color_peaks += peaks
            
            # Color richness score
            color_richness = min(1.0, total_color_variance / self.detection_params['min_color_diversity'])
            
        else:
            total_color_variance = np.var(roi)
            color_peaks = 0
            color_richness = min(1.0, total_color_variance / 500.0)
        
        return {
            'total_color_variance': total_color_variance,
            'color_peaks': color_peaks,
            'color_richness': color_richness,
            'has_diverse_colors': total_color_variance > self.detection_params['min_color_diversity']
        }
    
    def _analyze_texture_patterns(self, gray: np.ndarray) -> Dict:
        """
        Analyze texture patterns
        """
        # Gradient analysis
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        texture_strength = np.mean(gradient_magnitude)
        
        # Local texture analysis
        kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]], dtype=np.float32)
        texture_response = cv2.filter2D(gray, -1, kernel)
        texture_variance = np.var(texture_response)
        
        # Texture score
        texture_score = min(1.0, texture_strength / self.detection_params['min_texture_strength'])
        
        return {
            'texture_strength': texture_strength,
            'texture_variance': texture_variance,
            'texture_score': texture_score,
            'has_texture': texture_strength > self.detection_params['min_texture_strength']
        }
    
    def _analyze_structure(self, gray: np.ndarray) -> Dict:
        """
        Analyze structural elements
        """
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Corner detection
        try:
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.01, minDistance=10)
            corner_count = len(corners) if corners is not None else 0
        except:
            corner_count = 0
        
        return {
            'edge_density': edge_density,
            'corner_count': corner_count,
            'structure_score': edge_density * 10 + corner_count / 20.0,
            'has_structure': edge_density > self.detection_params['edge_density_threshold']
        }
    
    def _calculate_improved_confidence(self, analysis: Dict) -> Dict:
        """
        Calculate confidence with improved empty detection logic for supermarket videos
        """
        uniformity = analysis['uniformity']
        objects = analysis['objects']
        color = analysis['color']
        texture = analysis['texture']
        structure = analysis['structure']
        
        # Enhanced empty indicators for supermarket videos
        is_uniform = uniformity['is_uniform']
        has_few_objects = objects['meaningful_object_count'] <= 1
        low_color_diversity = not color['has_diverse_colors']
        low_texture = not texture['has_texture']
        minimal_structure = not structure['has_structure']
        
        # Additional supermarket-specific indicators
        supermarket_empty_indicators = []
        
        if self.detection_params.get('supermarket_mode', False):
            # Check for shelf background patterns (common in supermarkets)
            shelf_background_detected = (
                uniformity['total_variance'] < self.detection_params['lighting_variance_threshold'] and
                objects['meaningful_object_count'] == 0
            )
            
            # Check for lighting uniformity typical of empty shelves
            lighting_uniformity = uniformity['uniformity_score'] > 0.75
            
            # Check for minimal edge content (empty shelves have clean lines)
            minimal_edges = objects['edge_density'] < self.detection_params['edge_density_threshold']
            
            supermarket_empty_indicators = [
                shelf_background_detected,
                lighting_uniformity,
                minimal_edges
            ]
        
        # Calculate empty confidence based on multiple indicators
        primary_empty_indicators = sum([
            is_uniform,
            has_few_objects,
            low_color_diversity,
            low_texture,
            minimal_structure
        ])
        
        supermarket_indicators_count = sum(supermarket_empty_indicators)
        total_empty_indicators = primary_empty_indicators + supermarket_indicators_count
        
        # Enhanced weighted scoring for supermarket videos
        if total_empty_indicators >= 5:  # Very strong empty indicators
            empty_confidence = 0.85 + min(0.15, (total_empty_indicators - 5) * 0.03)
            is_empty = True
        elif total_empty_indicators >= 3:  # Strong empty indicators
            empty_confidence = 0.65 + (total_empty_indicators - 3) * 0.1
            is_empty = True
        elif total_empty_indicators >= 2:  # Moderate empty indicators
            empty_confidence = 0.45 + (total_empty_indicators - 2) * 0.1
            is_empty = total_empty_indicators >= 3  # More conservative for supermarket videos
        else:  # Likely has products
            is_empty = False
            # Calculate fullness confidence with video compression adjustment
            compression_factor = self.detection_params.get('video_compression_factor', 1.0)
            fullness_score = (
                objects['object_density'] * 0.4 +
                color['color_richness'] * 0.3 +
                texture['texture_score'] * 0.2 +
                structure['structure_score'] / 5.0 * 0.1
            ) * compression_factor
            empty_confidence = min(1.0, fullness_score)
        
        # Apply sensitivity adjustment with supermarket mode consideration
        if is_empty:
            sensitivity_boost = 1.0 + self.sensitivity * 0.3  # Reduced boost for supermarket mode
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
                'structure_analysis': min(1.0, structure['structure_score'] / 5.0)
            },
            'empty_indicators': total_empty_indicators,
            'supermarket_indicators': supermarket_indicators_count
        }
    
    def _determine_visual_state(self, confidence: float, is_empty: bool) -> str:
        """Determine visual state based on confidence"""
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
        """Determine alert level"""
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
        """Calculate stability and trend metrics"""
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
        """Enhanced alert triggering logic"""
        if not confidence_data['is_empty'] or alert_level == 'NONE':
            return False
        
        if confidence_data['empty_confidence'] < 0.5:
            return False
        
        if stability_data['consistency_score'] < 2:
            return False
        
        if timestamp - self.alert_cooldown[shelf_name] < self.cooldown_time:
            return False
        
        self.alert_cooldown[shelf_name] = timestamp
        return True
    
    def _get_visual_feedback_data(self, visual_state: str, alert_level: str) -> Dict:
        """Get visual feedback configuration"""
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
            'method_scores': {method: 0.0 for method in ['uniformity_analysis', 'object_detection', 
                                                        'color_analysis', 'texture_analysis', 'structure_analysis']},
            'frame_count': self.frame_count,
            'timestamp': time.time(),
            'trend': 'UNKNOWN'
        }
