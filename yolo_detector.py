"""
YOLO-based Object Detection Module
Uses YOLO models for enhanced product and shelf detection
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple
import logging
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, config: Dict):
        self.config = config
        self.detection_config = config['detection']
        self.logger = logging.getLogger(__name__)
        
        # Initialize YOLO model
        try:
            model_path = self.detection_config.get('yolo_model', 'yolov8n.pt')
            self.model = YOLO(model_path)
            self.logger.info(f"YOLO model loaded: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame using YOLO
        Returns list of detected objects with bounding boxes and confidence
        """
        if self.model is None:
            return []
        
        try:
            # Run YOLO inference
            results = self.model(frame)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Filter by confidence threshold
                        if confidence >= self.detection_config['confidence_threshold']:
                            detection = {
                                'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],  # x, y, w, h
                                'confidence': float(confidence),
                                'class_id': class_id,
                                'class_name': self.model.names[class_id] if class_id < len(self.model.names) else 'unknown'
                            }
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"YOLO detection failed: {e}")
            return []
    
    def filter_shelf_related_objects(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detections for shelf-related objects (food items, bottles, etc.)
        """
        # Common COCO classes that might be found on store shelves
        shelf_classes = [
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'person', 'book', 'clock',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        filtered_detections = []
        for detection in detections:
            if detection['class_name'].lower() in [cls.lower() for cls in shelf_classes]:
                filtered_detections.append(detection)
        
        return filtered_detections
    
    def analyze_section_with_yolo(self, roi: np.ndarray, section_name: str) -> Dict:
        """
        Analyze a shelf section using YOLO to detect products
        """
        if roi is None or roi.size == 0:
            return {
                'product_count': 0,
                'detections': [],
                'is_empty': True,
                'confidence': 1.0
            }
        
        # Detect objects in the ROI
        detections = self.detect_objects(roi)
        shelf_objects = self.filter_shelf_related_objects(detections)
        
        # Determine if section is empty based on object count
        product_count = len(shelf_objects)
        is_empty = product_count == 0
        
        # Calculate confidence based on detection scores
        if shelf_objects:
            avg_confidence = np.mean([det['confidence'] for det in shelf_objects])
        else:
            avg_confidence = 1.0 if is_empty else 0.0
        
        return {
            'product_count': product_count,
            'detections': shelf_objects,
            'is_empty': is_empty,
            'confidence': float(avg_confidence)
        }
    
    def visualize_yolo_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw YOLO detections on frame
        """
        result = frame.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            x, y, w, h = bbox
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Draw bounding box
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 255), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(result, (x, y - label_size[1] - 10), (x + label_size[0], y), (255, 0, 255), -1)
            cv2.putText(result, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return result
    
    def get_section_product_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of shelf sections to expected product types
        This can be customized based on store layout
        """
        return {
            'bread': ['sandwich', 'donut', 'cake'],
            'milk': ['bottle', 'cup'],
            'cereals': ['bowl', 'spoon'],
            'snacks': ['banana', 'apple', 'orange', 'sandwich']
        }
