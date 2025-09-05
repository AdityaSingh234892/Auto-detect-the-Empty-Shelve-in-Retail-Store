"""
Configuration Manager
Utility for managing and updating shelf monitoring configuration
"""
import yaml
import json
from typing import Dict, List, Tuple
import cv2
import numpy as np

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file {self.config_path} not found")
            return {}
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)
    
    def add_shelf_section(self, name: str, region: List[int], 
                         threshold: float = 0.3, color: List[int] = None):
        """Add a new shelf section"""
        if color is None:
            color = [0, 255, 0]  # Default green
        
        if 'shelf_sections' not in self.config:
            self.config['shelf_sections'] = {}
        
        self.config['shelf_sections'][name] = {
            'region': region,
            'threshold': threshold,
            'color': color
        }
        
        print(f"Added shelf section: {name}")
    
    def remove_shelf_section(self, name: str):
        """Remove a shelf section"""
        if 'shelf_sections' in self.config and name in self.config['shelf_sections']:
            del self.config['shelf_sections'][name]
            print(f"Removed shelf section: {name}")
        else:
            print(f"Shelf section '{name}' not found")
    
    def update_detection_params(self, **kwargs):
        """Update detection parameters"""
        if 'detection' not in self.config:
            self.config['detection'] = {}
        
        for key, value in kwargs.items():
            self.config['detection'][key] = value
            print(f"Updated detection parameter: {key} = {value}")
    
    def interactive_setup(self, sample_frame_path: str = None):
        """Interactive setup using a sample frame"""
        if sample_frame_path:
            frame = cv2.imread(sample_frame_path)
            if frame is None:
                print(f"Could not load sample frame: {sample_frame_path}")
                return
            
            print("Interactive setup mode")
            print("Click and drag to define shelf regions")
            print("Press 's' to save region, 'q' to quit")
            
            regions = []
            
            def mouse_callback(event, x, y, flags, param):
                nonlocal regions
                if event == cv2.EVENT_LBUTTONDOWN:
                    param['start_point'] = (x, y)
                elif event == cv2.EVENT_LBUTTONUP:
                    end_point = (x, y)
                    start_point = param['start_point']
                    
                    # Calculate region
                    x1, y1 = start_point
                    x2, y2 = end_point
                    region = [min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)]
                    
                    # Ask for section name
                    section_name = input("Enter section name: ")
                    regions.append((section_name, region))
                    
                    print(f"Added region for {section_name}: {region}")
            
            # Setup mouse callback
            param = {}
            cv2.namedWindow('Setup')
            cv2.setMouseCallback('Setup', mouse_callback, param)
            
            while True:
                display_frame = frame.copy()
                
                # Draw existing regions
                for name, region in regions:
                    x, y, w, h = region
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(display_frame, name, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Setup', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save all regions
                    for name, region in regions:
                        self.add_shelf_section(name, region)
                    self.save_config()
                    print("Configuration saved")
                    break
            
            cv2.destroyAllWindows()

def create_sample_config():
    """Create a sample configuration file"""
    config = {
        'video': {
            'source': 0,
            'width': 1280,
            'height': 720,
            'fps': 30
        },
        'shelf_sections': {
            'bread': {
                'region': [100, 150, 200, 100],
                'threshold': 0.3,
                'color': [0, 255, 0]
            },
            'milk': {
                'region': [350, 150, 200, 100],
                'threshold': 0.3,
                'color': [255, 0, 0]
            },
            'cereals': {
                'region': [600, 150, 200, 100],
                'threshold': 0.3,
                'color': [0, 0, 255]
            }
        },
        'detection': {
            'canny_low': 50,
            'canny_high': 150,
            'min_contour_area': 1000,
            'max_contour_area': 50000,
            'empty_threshold': 0.7,
            'yolo_model': 'yolov8n.pt',
            'confidence_threshold': 0.5
        },
        'alerts': {
            'display_duration': 3000,
            'sound_enabled': True,
            'sound_file': 'alert.wav',
            'log_enabled': True,
            'log_file': 'shelf_alerts.log'
        },
        'display': {
            'show_regions': True,
            'show_contours': True,
            'alert_text_size': 1.0,
            'alert_text_color': [0, 0, 255],
            'alert_text_thickness': 2
        }
    }
    
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    print("Sample configuration created: config.yaml")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-sample":
        create_sample_config()
    else:
        config_manager = ConfigManager()
        
        # Example usage
        print("Configuration Manager")
        print("Available sections:", list(config_manager.config.get('shelf_sections', {}).keys()))
        
        # Interactive mode if sample frame is provided
        if len(sys.argv) > 1:
            config_manager.interactive_setup(sys.argv[1])
