"""
Empty Section Detection Module
Analyzes shelf sections to determine if they are empty
"""
import cv2
import numpy as np
from typing import Dict, Tuple
import logging

class EmptyDetector:
    def __init__(self, config: Dict):
        self.config = config
        self.detection_config = config['detection']
        self.logger = logging.getLogger(__name__)
        
    def is_section_empty(self, roi: np.ndarray, threshold: float = 0.7) -> Tuple[bool, float]:
        """
        Determine if a section is empty based on various visual cues
        Returns (is_empty, confidence_score)
        """
        if roi is None or roi.size == 0:
            return True, 1.0
        
        # Method 1: Analyze pixel intensity variance
        empty_score_variance = self._analyze_pixel_variance(roi)
        
        # Method 2: Analyze color distribution
        empty_score_color = self._analyze_color_distribution(roi)
        
        # Method 3: Analyze edge density
        empty_score_edges = self._analyze_edge_density(roi)
        
        # Method 4: Analyze texture features
        empty_score_texture = self._analyze_texture(roi)
        
        # Combine scores (weighted average)
        weights = [0.3, 0.2, 0.3, 0.2]
        combined_score = (
            weights[0] * empty_score_variance +
            weights[1] * empty_score_color +
            weights[2] * empty_score_edges +
            weights[3] * empty_score_texture
        )
        
        is_empty = combined_score > threshold
        
        self.logger.debug(f"Empty detection scores - Variance: {empty_score_variance:.2f}, "
                         f"Color: {empty_score_color:.2f}, Edges: {empty_score_edges:.2f}, "
                         f"Texture: {empty_score_texture:.2f}, Combined: {combined_score:.2f}")
        
        return is_empty, combined_score
    
    def _analyze_pixel_variance(self, roi: np.ndarray) -> float:
        """
        Analyze pixel intensity variance - empty shelves typically have low variance
        """
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Calculate variance
        variance = np.var(gray)
        
        # Normalize variance (empty shelves have low variance)
        # Higher score means more likely to be empty
        max_variance = 10000  # Empirical value
        normalized_variance = 1.0 - min(variance / max_variance, 1.0)
        
        return normalized_variance
    
    def _analyze_color_distribution(self, roi: np.ndarray) -> float:
        """
        Analyze color distribution - empty shelves have uniform colors
        """
        # Calculate color histogram
        hist_b = cv2.calcHist([roi], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([roi], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([roi], [2], None, [256], [0, 256])
        
        # Calculate histogram concentration (how concentrated the colors are)
        def histogram_concentration(hist):
            total_pixels = np.sum(hist)
            if total_pixels == 0:
                return 1.0
            
            # Find the peak and calculate concentration around it
            max_bin = np.argmax(hist)
            peak_range = 20  # Range around peak
            start_bin = max(0, max_bin - peak_range)
            end_bin = min(256, max_bin + peak_range)
            
            concentrated_pixels = np.sum(hist[start_bin:end_bin])
            concentration = concentrated_pixels / total_pixels
            
            return concentration
        
        # Average concentration across all channels
        concentrations = [
            histogram_concentration(hist_b),
            histogram_concentration(hist_g),
            histogram_concentration(hist_r)
        ]
        
        avg_concentration = np.mean(concentrations)
        return avg_concentration
    
    def _analyze_edge_density(self, roi: np.ndarray) -> float:
        """
        Analyze edge density - empty shelves have fewer edges
        """
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate edge density
        total_pixels = gray.shape[0] * gray.shape[1]
        edge_pixels = np.sum(edges > 0)
        edge_density = edge_pixels / total_pixels
        
        # Empty shelves have low edge density
        # Invert the score so higher means more likely to be empty
        max_edge_density = 0.3  # Empirical value
        normalized_density = 1.0 - min(edge_density / max_edge_density, 1.0)
        
        return normalized_density
    
    def _analyze_texture(self, roi: np.ndarray) -> float:
        """
        Analyze texture using Local Binary Pattern-like approach
        """
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Simple texture analysis using standard deviation of gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        texture_score = np.std(gradient_magnitude)
        
        # Normalize texture score (empty shelves have low texture)
        max_texture = 50  # Empirical value
        normalized_texture = 1.0 - min(texture_score / max_texture, 1.0)
        
        return normalized_texture
    
    def analyze_section_details(self, roi: np.ndarray) -> Dict:
        """
        Provide detailed analysis of a section
        """
        if roi is None or roi.size == 0:
            return {
                'is_empty': True,
                'confidence': 1.0,
                'details': 'No ROI data'
            }
        
        # Get individual scores
        variance_score = self._analyze_pixel_variance(roi)
        color_score = self._analyze_color_distribution(roi)
        edge_score = self._analyze_edge_density(roi)
        texture_score = self._analyze_texture(roi)
        
        # Calculate overall emptiness
        is_empty, confidence = self.is_section_empty(roi)
        
        return {
            'is_empty': is_empty,
            'confidence': confidence,
            'variance_score': variance_score,
            'color_score': color_score,
            'edge_score': edge_score,
            'texture_score': texture_score,
            'mean_intensity': np.mean(roi),
            'std_intensity': np.std(roi)
        }
