"""
Main Shelf Monitoring System
Integrates all components for real-time shelf monitoring and empty section detection
"""
import cv2
import numpy as np
import yaml
import logging
import time
import argparse
from typing import Dict, List
import os

from shelf_detector import ShelfDetector
from empty_detector import EmptyDetector
from yolo_detector import YOLODetector
from alert_system import AlertSystem

class ShelfMonitoringSystem:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the shelf monitoring system
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.shelf_detector = ShelfDetector(self.config)
        self.empty_detector = EmptyDetector(self.config)
        self.yolo_detector = YOLODetector(self.config)
        self.alert_system = AlertSystem(self.config)
        
        # Video capture setup
        self.cap = None
        self.frame_count = 0
        self.fps = self.config['video']['fps']
        
        self.logger.info("Shelf Monitoring System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using default configuration.")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration if config file is not available"""
        return {
            'video': {'source': 0, 'width': 1280, 'height': 720, 'fps': 30},
            'shelf_sections': {
                'bread': {'region': [100, 150, 200, 100], 'threshold': 0.3, 'color': [0, 255, 0]},
                'milk': {'region': [350, 150, 200, 100], 'threshold': 0.3, 'color': [255, 0, 0]},
            },
            'detection': {
                'canny_low': 50, 'canny_high': 150, 'min_contour_area': 1000,
                'max_contour_area': 50000, 'empty_threshold': 0.7,
                'yolo_model': 'yolov8n.pt', 'confidence_threshold': 0.5
            },
            'alerts': {
                'display_duration': 3000, 'sound_enabled': False,
                'log_enabled': True, 'log_file': 'shelf_alerts.log'
            },
            'display': {
                'show_regions': True, 'show_contours': True,
                'alert_text_size': 1.0, 'alert_text_color': [0, 0, 255],
                'alert_text_thickness': 2
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_video_capture(self, source=None):
        """
        Initialize video capture from camera or file
        """
        if source is None:
            source = self.config['video']['source']
        
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {source}")
        
        # Set video properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['video']['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['video']['height'])
        self.cap.set(cv2.CAP_PROP_FPS, self.config['video']['fps'])
        
        self.logger.info(f"Video capture initialized with source: {source}")
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame for shelf monitoring
        """
        results = {}
        
        # Get configured shelf sections
        sections = self.shelf_detector.get_configured_sections()
        
        # Analyze each section
        for section in sections:
            section_name = section['name']
            region = section['region']
            threshold = section['threshold']
            
            # Extract region of interest
            roi = self.shelf_detector.extract_section_roi(frame, region)
            
            if roi is None or roi.size == 0:
                continue
            
            # Traditional empty detection
            is_empty_traditional, confidence_traditional = self.empty_detector.is_section_empty(
                roi, threshold
            )
            
            # YOLO-based detection
            yolo_result = self.yolo_detector.analyze_section_with_yolo(roi, section_name)
            is_empty_yolo = yolo_result['is_empty']
            confidence_yolo = yolo_result['confidence']
            
            # Combine results (weighted average)
            # Give more weight to traditional detection for empty shelf detection
            # and YOLO for product identification
            combined_confidence = (0.7 * confidence_traditional + 0.3 * confidence_yolo)
            is_empty_combined = is_empty_traditional or (is_empty_yolo and confidence_yolo > 0.5)
            
            # Store results
            results[section_name] = {
                'is_empty': is_empty_combined,
                'confidence': combined_confidence,
                'traditional_result': {
                    'is_empty': is_empty_traditional,
                    'confidence': confidence_traditional
                },
                'yolo_result': yolo_result,
                'roi_shape': roi.shape if roi is not None else None
            }
            
            # Trigger alert if section is empty
            if is_empty_combined and combined_confidence > threshold:
                self.alert_system.trigger_alert(section_name, combined_confidence)
            else:
                self.alert_system.clear_alert(section_name)
        
        return results
    
    def visualize_frame(self, frame: np.ndarray, analysis_results: Dict) -> np.ndarray:
        """
        Add visualizations to the frame
        """
        result = frame.copy()
        
        # Get sections for visualization
        sections = self.shelf_detector.get_configured_sections()
        
        # Draw section status
        result = self.alert_system.draw_section_status(result, sections, analysis_results)
        
        # Draw alerts
        result = self.alert_system.draw_alerts_on_frame(result)
        
        # Add system info
        result = self._draw_system_info(result)
        
        return result
    
    def _draw_system_info(self, frame: np.ndarray) -> np.ndarray:
        """Draw system information on frame"""
        result = frame.copy()
        
        # System info
        info_text = [
            f"Frame: {self.frame_count}",
            f"FPS: {self.fps}",
            f"Active Alerts: {len(self.alert_system.active_alerts)}",
            f"Press 'q' to quit, 'r' to reset alerts"
        ]
        
        y_start = frame.shape[0] - 100
        for i, text in enumerate(info_text):
            y_pos = y_start + i * 20
            cv2.putText(result, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
        
        return result
    
    def run_realtime(self):
        """
        Run real-time shelf monitoring
        """
        try:
            self.initialize_video_capture()
            
            self.logger.info("Starting real-time shelf monitoring...")
            self.logger.info("Press 'q' to quit, 'r' to reset alerts, 's' to save frame")
            
            frame_time = 1.0 / self.fps
            
            while True:
                start_time = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.warning("Failed to read frame from video source")
                    break
                
                self.frame_count += 1
                
                # Process frame
                analysis_results = self.process_frame(frame)
                
                # Visualize results
                display_frame = self.visualize_frame(frame, analysis_results)
                
                # Display frame
                cv2.imshow('Shelf Monitoring System', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset alerts
                    self.alert_system.active_alerts.clear()
                    self.logger.info("Alerts reset")
                elif key == ord('s'):
                    # Save current frame
                    filename = f"shelf_monitor_frame_{self.frame_count}.jpg"
                    cv2.imwrite(filename, display_frame)
                    self.logger.info(f"Frame saved as {filename}")
                
                # Control frame rate
                elapsed_time = time.time() - start_time
                if elapsed_time < frame_time:
                    time.sleep(frame_time - elapsed_time)
        
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error during monitoring: {e}")
        finally:
            self.cleanup()
    
    def process_video_file(self, video_path: str, output_path: str = None):
        """
        Process a video file and save results
        """
        try:
            self.initialize_video_capture(video_path)
            
            if output_path is None:
                output_path = f"processed_{os.path.basename(video_path)}"
            
            # Get video properties
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            self.logger.info(f"Processing video: {video_path}")
            self.logger.info(f"Output will be saved to: {output_path}")
            self.logger.info(f"Total frames: {total_frames}")
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                self.frame_count += 1
                
                # Process frame
                analysis_results = self.process_frame(frame)
                
                # Visualize results
                display_frame = self.visualize_frame(frame, analysis_results)
                
                # Write frame to output video
                out.write(display_frame)
                
                # Show progress
                if self.frame_count % 30 == 0:
                    progress = (self.frame_count / total_frames) * 100
                    self.logger.info(f"Progress: {progress:.1f}% ({self.frame_count}/{total_frames})")
            
            out.release()
            self.logger.info(f"Video processing completed. Output saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing video: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Clean up resources
        """
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Save alert log
        if hasattr(self.alert_system, 'alert_history') and self.alert_system.alert_history:
            log_file = self.alert_system.export_alert_log()
            self.logger.info(f"Alert log saved to: {log_file}")
        
        self.logger.info("Cleanup completed")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Shelf Monitoring System")
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path')
    parser.add_argument('--video', '-v', 
                       help='Video file to process (if not provided, uses camera)')
    parser.add_argument('--output', '-o', 
                       help='Output video path (for video file processing)')
    
    args = parser.parse_args()
    
    # Create monitoring system
    monitor = ShelfMonitoringSystem(args.config)
    
    try:
        if args.video:
            # Process video file
            monitor.process_video_file(args.video, args.output)
        else:
            # Run real-time monitoring
            monitor.run_realtime()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    main()
