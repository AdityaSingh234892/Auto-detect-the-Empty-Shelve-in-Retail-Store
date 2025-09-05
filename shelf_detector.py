"""
Shelf Detection Module
Handles shelf and section detection using OpenCV techniques
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
import logging

class ShelfDetector:
    def __init__(self, config: Dict):
        self.config = config
        self.detection_config = config['detection']
        self.logger = logging.getLogger(__name__)
        
    def detect_shelves_contours(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect shelf regions using contour detection
        Returns list of bounding boxes (x, y, w, h)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 
                         self.detection_config['canny_low'], 
                         self.detection_config['canny_high'])
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shelf_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if (self.detection_config['min_contour_area'] < area < 
                self.detection_config['max_contour_area']):
                x, y, w, h = cv2.boundingRect(contour)
                # Filter for horizontal shelf-like shapes
                if w > h * 1.5:  # Width should be significantly larger than height
                    shelf_regions.append((x, y, w, h))
        
        return shelf_regions
    
    def detect_shelves_lines(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect shelf regions using line detection (Hough transform)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 
                         self.detection_config['canny_low'], 
                         self.detection_config['canny_high'])
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                               minLineLength=100, maxLineGap=10)
        
        shelf_regions = []
        if lines is not None:
            # Group horizontal lines to form shelf regions
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:  # Nearly horizontal line
                    horizontal_lines.append((min(x1, x2), y1, abs(x2 - x1), 50))
            
            # Merge nearby lines
            horizontal_lines.sort(key=lambda x: x[1])  # Sort by y-coordinate
            merged_regions = []
            
            for line in horizontal_lines:
                x, y, w, h = line
                merged = False
                for i, region in enumerate(merged_regions):
                    rx, ry, rw, rh = region
                    if abs(y - ry) < 30:  # Lines are close vertically
                        # Merge lines
                        new_x = min(x, rx)
                        new_w = max(x + w, rx + rw) - new_x
                        merged_regions[i] = (new_x, min(y, ry), new_w, h)
                        merged = True
                        break
                
                if not merged:
                    merged_regions.append(line)
            
            shelf_regions = merged_regions
        
        return shelf_regions
    
    def get_configured_sections(self) -> List[Dict]:
        """
        Get shelf sections from configuration
        """
        sections = []
        for product_name, section_config in self.config['shelf_sections'].items():
            section = {
                'name': product_name,
                'region': section_config['region'],
                'threshold': section_config['threshold'],
                'color': section_config['color']
            }
            sections.append(section)
        return sections
    
    def extract_section_roi(self, frame: np.ndarray, region: List[int]) -> np.ndarray:
        """
        Extract region of interest from frame
        """
        x, y, w, h = region
        return frame[y:y+h, x:x+w]
    
    def visualize_detections(self, frame: np.ndarray, regions: List[Tuple[int, int, int, int]], 
                           color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Draw detected regions on frame
        """
        result = frame.copy()
        for x, y, w, h in regions:
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
        return result
