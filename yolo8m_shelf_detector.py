"""
YOLOv8m-Enhanced Empty Shelf Detector
Advanced detection with YOLOv8m model for superior empty shelf identification in supermarket videos
"""
import os

# Fix OpenMP library conflict (must be before other imports)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
import time
from typing import Dict, Tuple, List
import logging

class YOLOv8mShelfDetector:
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.detection_history = {}
        self.alert_cooldown = {}
        self.frame_count = 0
        self.yolo_model = None
        
        # Initialize YOLOv8m model
        self._initialize_yolo_model()
        
        # ENHANCED detection parameters for improved empty shelf detection
        self.detection_params = {
            'min_object_area': 200,           # Reduced for better sensitivity
            'max_empty_variance': 200,        # Increased for more tolerance
            'min_color_diversity': 600,       # Reduced for better empty detection
            'min_texture_strength': 6,        # Reduced for better empty detection
            'edge_density_threshold': 0.022,  # Increased for more tolerance
            'uniformity_threshold': 0.75,     # Reduced for better empty detection
            'contrast_threshold': 15,         # Reduced for better sensitivity
            'supermarket_mode': True,         # Special handling for supermarket videos
            'video_compression_factor': 0.85, # Increased compensation
            'lighting_variance_threshold': 120, # Increased tolerance
            'shelf_background_tolerance': 0.16, # Increased tolerance
            'yolo_confidence_threshold': 0.20,  # Reduced for more sensitive YOLO detection
            'empty_confidence_boost': 0.12,    # Increased boost for empty detection
            'product_detection_weight': 0.60   # Slightly reduced weight for YOLO
        }
        
        # Product categories that indicate stocked shelves
        self.product_classes = {
            'bottle', 'cup', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 
            'potted plant', 'vase', 'scissors', 'toothbrush', 'book',
            'cell phone', 'laptop', 'mouse', 'remote', 'keyboard', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'clock', 'teddy bear',
            'hair drier', 'toothbrush', 'wine glass', 'fork', 'knife', 'spoon'
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
        
        # History tracking
        self.history_length = 15  # Increased for better trending
        self.cooldown_time = 1.0  # Reduced for faster response
        
        print("🎯 YOLOv8m-Enhanced Shelf Detector initialized for supermarket videos")
    
    def _initialize_yolo_model(self):
        """Initialize YOLOv8m model"""
        try:
            # Try to import ultralytics (YOLOv8)
            from ultralytics import YOLO
            
            # Load YOLOv8m model
            print("📥 Loading YOLOv8m model...")
            self.yolo_model = YOLO('yolov8m.pt')  # Will download if not present
            print("✅ YOLOv8m model loaded successfully")
            
        except ImportError:
            print("⚠️ Ultralytics not found. Installing YOLOv8...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
                from ultralytics import YOLO
                self.yolo_model = YOLO('yolov8m.pt')
                print("✅ YOLOv8m installed and loaded successfully")
            except Exception as e:
                print(f"❌ Failed to install/load YOLOv8m: {e}")
                print("🔄 Falling back to traditional detection methods")
                self.yolo_model = None
        except Exception as e:
            print(f"❌ Error loading YOLOv8m: {e}")
            print("🔄 Using traditional detection methods")
            self.yolo_model = None
    
    def analyze_shelf_region(self, roi: np.ndarray, shelf_name: str, 
                           timestamp: float = None) -> Dict:
        """
        Advanced analysis with YOLOv8m integration for superior empty shelf detection
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
        
        # Perform YOLOv8m-enhanced analysis
        analysis_results = self._perform_yolo_enhanced_analysis(roi)
        
        # Calculate confidence with YOLOv8m integration
        confidence_data = self._calculate_yolo_enhanced_confidence(analysis_results)
        
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
            'frame_number': self.frame_count,
            'yolo_products': analysis_results.get('yolo', {}).get('products_detected', [])
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
            'yolo_products': detection_record['yolo_products']
        }
    
    def _perform_yolo_enhanced_analysis(self, roi: np.ndarray) -> Dict:
        """
        Perform comprehensive analysis with YOLOv8m integration
        """
        # Convert to grayscale for traditional analysis
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Traditional analysis methods
        uniformity_analysis = self._analyze_uniformity(roi, gray)
        color_analysis = self._advanced_color_analysis(roi)
        texture_analysis = self._analyze_texture(gray)
        structure_analysis = self._analyze_structure(gray)
        
        # YOLOv8m object detection
        yolo_analysis = self._perform_yolo_detection(roi)
        
        # Enhanced object detection combining traditional + YOLO
        object_analysis = self._detect_enhanced_objects(roi, gray, yolo_analysis)
        
        return {
            'uniformity': uniformity_analysis,
            'objects': object_analysis,
            'color': color_analysis,
            'texture': texture_analysis,
            'structure': structure_analysis,
            'yolo': yolo_analysis,
            'roi_shape': roi.shape
        }
    
    def _perform_yolo_detection(self, roi: np.ndarray) -> Dict:
        """
        Perform YOLOv8m object detection on the shelf region
        """
        if self.yolo_model is None:
            return {
                'products_detected': [],
                'product_count': 0,
                'confidence_scores': [],
                'detection_areas': [],
                'coverage_ratio': 0.0,
                'yolo_available': False
            }
        
        try:
            # Run YOLOv8m inference
            results = self.yolo_model(roi, conf=self.detection_params['yolo_confidence_threshold'], verbose=False)
            
            products_detected = []
            confidence_scores = []
            detection_areas = []
            
            if results and len(results) > 0:
                for result in results:
                    if result.boxes is not None:
                        for box in result.boxes:
                            # Get class name
                            class_id = int(box.cls[0])
                            class_name = self.yolo_model.names[class_id]
                            confidence = float(box.conf[0])
                            
                            # Check if it's a product class
                            if class_name.lower() in self.product_classes and confidence > self.detection_params['yolo_confidence_threshold']:
                                # Get bounding box
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                area = (x2 - x1) * (y2 - y1)
                                
                                products_detected.append({
                                    'class': class_name,
                                    'confidence': confidence,
                                    'bbox': (x1, y1, x2, y2),
                                    'area': area
                                })
                                confidence_scores.append(confidence)
                                detection_areas.append(area)
            
            # Calculate coverage ratio
            roi_area = roi.shape[0] * roi.shape[1]
            total_detection_area = sum(detection_areas)
            coverage_ratio = min(1.0, total_detection_area / roi_area) if roi_area > 0 else 0.0
            
            return {
                'products_detected': products_detected,
                'product_count': len(products_detected),
                'confidence_scores': confidence_scores,
                'detection_areas': detection_areas,
                'coverage_ratio': coverage_ratio,
                'total_detection_area': total_detection_area,
                'yolo_available': True
            }
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return {
                'products_detected': [],
                'product_count': 0,
                'confidence_scores': [],
                'detection_areas': [],
                'coverage_ratio': 0.0,
                'yolo_available': False,
                'error': str(e)
            }
    
    def _detect_enhanced_objects(self, roi: np.ndarray, gray: np.ndarray, yolo_analysis: Dict) -> Dict:
        """
        Enhanced object detection combining traditional methods with YOLO results
        """
        # Traditional contour detection
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 15, 3)
        _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        combined_thresh = cv2.bitwise_and(adaptive_thresh, otsu_thresh)
        
        contours, _ = cv2.findContours(combined_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter meaningful objects
        meaningful_objects = []
        total_meaningful_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.detection_params['min_object_area']:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
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
        
        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.count_nonzero(edges)
        roi_area = roi.shape[0] * roi.shape[1]
        edge_density = edge_pixels / roi_area if roi_area > 0 else 0
        
        # Combine traditional and YOLO detection
        yolo_product_count = yolo_analysis.get('product_count', 0)
        yolo_coverage = yolo_analysis.get('coverage_ratio', 0.0)
        
        # Enhanced object density calculation
        traditional_density = min(1.0, len(meaningful_objects) * 0.2 + (total_meaningful_area / roi_area) * 2)
        yolo_density = min(1.0, yolo_product_count * 0.3 + yolo_coverage * 1.5)
        
        # Weight the densities based on YOLO availability
        if yolo_analysis.get('yolo_available', False):
            combined_density = (traditional_density * 0.4 + yolo_density * 0.6)
        else:
            combined_density = traditional_density
        
        coverage_ratio = total_meaningful_area / roi_area if roi_area > 0 else 0
        
        return {
            'meaningful_object_count': len(meaningful_objects),
            'total_meaningful_area': total_meaningful_area,
            'coverage_ratio': coverage_ratio,
            'objects': meaningful_objects,
            'object_density': combined_density,
            'edge_density': edge_density,
            'yolo_enhanced': yolo_analysis.get('yolo_available', False),
            'yolo_product_count': yolo_product_count,
            'yolo_coverage': yolo_coverage
        }
    
    def _calculate_yolo_enhanced_confidence(self, analysis: Dict) -> Dict:
        """
        Calculate confidence with YOLOv8m integration for superior empty detection
        """
        uniformity = analysis['uniformity']
        objects = analysis['objects']
        color = analysis['color']
        texture = analysis['texture']
        structure = analysis['structure']
        yolo = analysis['yolo']
        
        # BALANCED empty indicators - not too strict, not too loose
        is_uniform = uniformity['is_uniform']
        has_few_objects = objects['meaningful_object_count'] <= 1  # Back to <= 1 for balance
        low_color_diversity = not color['has_diverse_colors']
        low_texture = not texture['has_texture']
        minimal_structure = not structure['has_structure']
        
        # YOLOv8m-based indicators - ENHANCED for empty detection
        yolo_no_products = yolo.get('product_count', 0) == 0
        yolo_low_coverage = yolo.get('coverage_ratio', 0.0) < 0.12  # Increased from 0.08 to 0.12 for better sensitivity
        yolo_available = yolo.get('yolo_available', False)
        
        # Enhanced supermarket-specific indicators
        supermarket_empty_indicators = []
        
        if self.detection_params.get('supermarket_mode', False):
            shelf_background_detected = (
                uniformity['total_variance'] < self.detection_params['lighting_variance_threshold'] and
                objects['meaningful_object_count'] == 0
            )
            lighting_uniformity = uniformity['uniformity_score'] > 0.70
            minimal_edges = objects['edge_density'] < self.detection_params['edge_density_threshold']
            
            supermarket_empty_indicators = [
                shelf_background_detected,
                lighting_uniformity,
                minimal_edges
            ]
        
        # Calculate empty confidence with YOLOv8m weighting
        primary_empty_indicators = [
            is_uniform,
            has_few_objects,
            low_color_diversity,
            low_texture,
            minimal_structure
        ]
        
        # YOLOv8m indicators (high weight when available)
        yolo_empty_indicators = [yolo_no_products, yolo_low_coverage] if yolo_available else []
        
        primary_count = sum(primary_empty_indicators)
        yolo_count = sum(yolo_empty_indicators)
        supermarket_count = sum(supermarket_empty_indicators)
        
        # ENHANCED scoring with YOLOv8m priority - IMPROVED for empty shelf detection
        if yolo_available:
            # YOLOv8m-enhanced scoring - MORE SENSITIVE TO EMPTY SHELVES
            if yolo_count >= 2 and primary_count >= 2:  # Strong evidence from both (reduced threshold)
                empty_confidence = 0.90 + min(0.10, primary_count * 0.02)
                is_empty = True
            elif yolo_count >= 2 and primary_count >= 1:  # Strong YOLO + minimal traditional (more sensitive)
                empty_confidence = 0.82 + (primary_count * 0.05) + (supermarket_count * 0.03)
                is_empty = True
            elif yolo_count >= 1 and primary_count >= 2:  # Moderate YOLO + moderate traditional (reduced threshold)
                empty_confidence = 0.72 + (primary_count * 0.05) + (supermarket_count * 0.04)
                is_empty = True
            elif primary_count >= 3 and supermarket_count >= 1:  # Strong traditional evidence (reduced threshold)
                empty_confidence = 0.68 + (primary_count - 3) * 0.05
                is_empty = True
            elif yolo_count >= 1 and primary_count >= 1:  # Lower threshold for empty detection
                empty_confidence = 0.62 + (primary_count * 0.04) + (supermarket_count * 0.03)
                is_empty = True
            elif primary_count >= 3:  # Traditional evidence only (reduced threshold)
                empty_confidence = 0.58 + (primary_count - 3) * 0.04 + (supermarket_count * 0.03)
                is_empty = True
            else:  # Likely has products
                is_empty = False
                # Enhanced fullness calculation with YOLO priority
                yolo_fullness = yolo.get('coverage_ratio', 0.0) * 2.5  # Balanced YOLO weight
                yolo_product_boost = min(0.4, yolo.get('product_count', 0) * 0.12)  # Product count bonus
                traditional_fullness = (
                    objects['object_density'] * 0.35 +
                    color['color_richness'] * 0.25 +
                    texture['texture_score'] * 0.20 +
                    structure['structure_score'] / 5.0 * 0.15
                )
                
                # Balanced calculation - neither too conservative nor too aggressive
                fullness_score = min(1.0, traditional_fullness * 0.4 + yolo_fullness * 0.5 + yolo_product_boost)
                empty_confidence = max(0.08, 1.0 - fullness_score * 1.1)  # Balanced empty confidence
        else:
            # Traditional scoring when YOLO not available - MORE SENSITIVE TO EMPTY SHELVES
            total_empty_indicators = primary_count + supermarket_count
            
            if total_empty_indicators >= 4:  # Strong evidence (reduced from 5)
                empty_confidence = 0.82 + min(0.15, (total_empty_indicators - 4) * 0.04)
                is_empty = True
            elif total_empty_indicators >= 3:  # Moderate evidence (reduced threshold)
                empty_confidence = 0.68 + (total_empty_indicators - 3) * 0.10
                is_empty = True
            elif total_empty_indicators >= 2:  # Some evidence - more sensitive threshold
                empty_confidence = 0.55 + (total_empty_indicators - 2) * 0.10
                is_empty = True
            else:
                is_empty = False
                # Balanced fullness calculation for traditional detection
                traditional_fullness = (
                    objects['object_density'] * 0.4 +
                    color['color_richness'] * 0.3 +
                    texture['texture_score'] * 0.2 +
                    structure['structure_score'] / 5.0 * 0.1
                )
                # More sensitive to empty detection
                empty_confidence = max(0.10, 1.0 - traditional_fullness * 1.05)
        
        # Apply sensitivity adjustment with empty confidence boost
        if is_empty:
            sensitivity_boost = 1.0 + self.sensitivity * 0.2
            empty_boost = self.detection_params.get('empty_confidence_boost', 0.0)
            empty_confidence = min(1.0, empty_confidence * sensitivity_boost + empty_boost)
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
                'structure_analysis': min(1.0, structure['structure_score'] / 5.0),
                'yolo_detection': yolo.get('coverage_ratio', 0.0) if yolo_available else 0.0
            },
            'empty_indicators': primary_count + supermarket_count,
            'yolo_indicators': yolo_count,
            'yolo_enhanced': yolo_available
        }
    
    # Include all the helper methods from the original detector
    def _analyze_uniformity(self, roi: np.ndarray, gray: np.ndarray) -> Dict:
        """Analyze uniformity - key indicator of empty shelves"""
        total_variance = np.var(gray)
        
        h, w = gray.shape
        patch_size = min(50, h//4, w//4)
        local_variances = []
        
        for y in range(0, h - patch_size, patch_size//2):
            for x in range(0, w - patch_size, patch_size//2):
                patch = gray[y:y+patch_size, x:x+patch_size]
                local_variances.append(np.var(patch))
        
        variance_std = np.std(local_variances) if local_variances else 0
        mean_local_variance = np.mean(local_variances) if local_variances else 0
        
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist / np.sum(hist)
        hist_entropy = -np.sum(hist_normalized * np.log(hist_normalized + 1e-7))
        
        uniformity_score = 1.0 / (1.0 + variance_std + mean_local_variance/100.0)
        
        return {
            'total_variance': total_variance,
            'local_variance_std': variance_std,
            'mean_local_variance': mean_local_variance,
            'histogram_entropy': hist_entropy,
            'uniformity_score': uniformity_score,
            'is_uniform': uniformity_score > self.detection_params['uniformity_threshold']
        }
    
    def _advanced_color_analysis(self, roi: np.ndarray) -> Dict:
        """Advanced color analysis for product detection"""
        if len(roi.shape) == 3:
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            color_variance_bgr = np.var(roi, axis=(0, 1))
            color_variance_hsv = np.var(hsv, axis=(0, 1))
            total_color_variance = np.sum(color_variance_bgr) + np.sum(color_variance_hsv)
            
            hist_b = cv2.calcHist([roi], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([roi], [1], None, [32], [0, 256])
            hist_r = cv2.calcHist([roi], [2], None, [32], [0, 256])
            
            color_richness = (np.count_nonzero(hist_b > hist_b.max() * 0.1) +
                            np.count_nonzero(hist_g > hist_g.max() * 0.1) +
                            np.count_nonzero(hist_r > hist_r.max() * 0.1)) / 96.0
        else:
            total_color_variance = np.var(roi)
            color_richness = 0.1
        
        has_diverse_colors = total_color_variance > self.detection_params['min_color_diversity']
        
        return {
            'total_color_variance': total_color_variance,
            'color_richness': min(1.0, color_richness),
            'has_diverse_colors': has_diverse_colors
        }
    
    def _analyze_texture(self, gray: np.ndarray) -> Dict:
        """Analyze texture using multiple methods"""
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobelx**2 + sobely**2)
        sobel_mean = np.mean(sobel_magnitude)
        
        texture_score = min(1.0, (laplacian_var + sobel_mean * 10) / 1000.0)
        has_texture = texture_score > (self.detection_params['min_texture_strength'] / 100.0)
        
        return {
            'laplacian_variance': laplacian_var,
            'sobel_magnitude_mean': sobel_mean,
            'texture_score': texture_score,
            'has_texture': has_texture
        }
    
    def _analyze_structure(self, gray: np.ndarray) -> Dict:
        """Analyze structural elements"""
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
        corner_count = len(corners) if corners is not None else 0
        
        lines = cv2.HoughLinesP(cv2.Canny(gray, 50, 150), 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        line_count = len(lines) if lines is not None else 0
        
        structure_score = corner_count + line_count * 2
        has_structure = structure_score > 20
        
        return {
            'corner_count': corner_count,
            'line_count': line_count,
            'structure_score': structure_score,
            'has_structure': has_structure
        }
    
    def update_sensitivity(self, new_sensitivity: float):
        """Update detection sensitivity"""
        self.sensitivity = max(0.1, min(0.9, new_sensitivity))
        print(f"🎯 Detection sensitivity updated to: {self.sensitivity:.2f}")
    
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
            return 'LOW'
        
        if confidence >= 0.85:
            return 'CRITICAL'
        elif confidence >= 0.70:
            return 'HIGH'
        elif confidence >= 0.55:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _should_trigger_alert(self, shelf_name: str, confidence_data: Dict, timestamp: float) -> bool:
        """Determine if alert should be triggered - BALANCED approach"""
        if not confidence_data['is_empty']:
            return False
        
        if timestamp - self.alert_cooldown.get(shelf_name, 0) < self.cooldown_time:
            return False
        
        confidence = confidence_data['empty_confidence']
        # ENHANCED threshold for alerts - more sensitive to empty shelves
        if confidence >= 0.65:  # Reduced from 0.75 to 0.65 for better empty detection
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
            if trend_slope > 0.1:
                return 'EMPTYING'
            elif trend_slope < -0.1:
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
