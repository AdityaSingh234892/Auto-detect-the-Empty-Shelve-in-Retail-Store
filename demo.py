"""
Demo and Testing Utilities
Provides tools for testing and demonstrating the shelf monitoring system
"""
import cv2
import numpy as np
import time
import random
from typing import Dict, List, Tuple

class DemoGenerator:
    """Generate demo scenarios for testing"""
    
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
    
    def create_sample_shelf_image(self, sections: List[Dict], scenario: str = "mixed") -> np.ndarray:
        """
        Create a synthetic shelf image for testing
        
        Args:
            sections: List of shelf section configurations
            scenario: "empty", "full", "mixed", or "random"
        """
        # Create base image (shelf background)
        image = np.ones((self.height, self.width, 3), dtype=np.uint8) * 200  # Light gray background
        
        # Draw shelf structure
        shelf_color = (139, 69, 19)  # Brown color for shelves
        
        # Horizontal shelf lines
        for y in [150, 250, 350, 450]:
            cv2.line(image, (0, y), (self.width, y), shelf_color, 5)
        
        # Vertical separators
        for x in range(100, self.width, 250):
            cv2.line(image, (x, 100), (x, 500), shelf_color, 3)
        
        # Fill sections based on scenario
        for section in sections:
            region = section['region']
            name = section['name']
            x, y, w, h = region
            
            if scenario == "empty":
                fill_level = 0.0
            elif scenario == "full":
                fill_level = 1.0
            elif scenario == "mixed":
                fill_level = 0.7 if name in ["bread", "milk"] else 0.1
            else:  # random
                fill_level = random.uniform(0.0, 1.0)
            
            self._draw_section_content(image, region, fill_level, name)
        
        return image
    
    def _draw_section_content(self, image: np.ndarray, region: List[int], 
                            fill_level: float, section_name: str):
        """Draw content in a shelf section"""
        x, y, w, h = region
        
        if fill_level < 0.1:
            # Empty section - just shelf background
            cv2.rectangle(image, (x, y), (x + w, y + h), (220, 220, 220), -1)
            return
        
        # Define colors for different products
        product_colors = {
            'bread': [(222, 184, 135), (160, 82, 45), (210, 180, 140)],  # Bread colors
            'milk': [(255, 255, 255), (245, 245, 245), (250, 250, 250)],  # Milk colors
            'cereals': [(255, 215, 0), (255, 140, 0), (255, 165, 0)],  # Cereal box colors
            'snacks': [(255, 20, 147), (0, 191, 255), (50, 205, 50)]  # Colorful snack packages
        }
        
        colors = product_colors.get(section_name, [(100, 100, 100)])
        
        # Fill section based on fill level
        filled_height = int(h * fill_level)
        products_area_y = y + h - filled_height
        
        # Draw empty space
        if filled_height < h:
            cv2.rectangle(image, (x, y), (x + w, products_area_y), (220, 220, 220), -1)
        
        # Draw products
        if filled_height > 0:
            num_products = max(1, int(fill_level * 8))  # Number of product items
            product_width = w // max(1, num_products)
            
            for i in range(num_products):
                product_x = x + i * product_width
                product_color = random.choice(colors)
                
                # Draw product rectangle with some variation
                product_h = filled_height + random.randint(-5, 5)
                product_w = product_width - 2
                
                cv2.rectangle(image, (product_x, products_area_y), 
                            (product_x + product_w, products_area_y + product_h), 
                            product_color, -1)
                
                # Add some texture/details
                cv2.rectangle(image, (product_x, products_area_y), 
                            (product_x + product_w, products_area_y + product_h), 
                            (0, 0, 0), 1)

class PerformanceTester:
    """Test system performance and accuracy"""
    
    def __init__(self, monitoring_system):
        self.system = monitoring_system
        self.test_results = []
    
    def test_detection_accuracy(self, test_scenarios: List[Tuple[str, Dict]]) -> Dict:
        """
        Test detection accuracy across different scenarios
        
        Args:
            test_scenarios: List of (scenario_name, expected_results) tuples
        """
        results = {
            'total_tests': len(test_scenarios),
            'correct_detections': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'accuracy': 0.0,
            'detailed_results': []
        }
        
        demo_gen = DemoGenerator()
        sections = self.system.shelf_detector.get_configured_sections()
        
        for scenario_name, expected in test_scenarios:
            # Generate test image
            if scenario_name == "all_empty":
                test_image = demo_gen.create_sample_shelf_image(sections, "empty")
            elif scenario_name == "all_full":
                test_image = demo_gen.create_sample_shelf_image(sections, "full")
            elif scenario_name == "mixed":
                test_image = demo_gen.create_sample_shelf_image(sections, "mixed")
            else:
                test_image = demo_gen.create_sample_shelf_image(sections, "random")
            
            # Process image
            detected = self.system.process_frame(test_image)
            
            # Compare results
            test_result = self._compare_results(detected, expected, scenario_name)
            results['detailed_results'].append(test_result)
            
            if test_result['correct']:
                results['correct_detections'] += 1
            else:
                if test_result['type'] == 'false_positive':
                    results['false_positives'] += 1
                else:
                    results['false_negatives'] += 1
        
        results['accuracy'] = results['correct_detections'] / results['total_tests']
        return results
    
    def _compare_results(self, detected: Dict, expected: Dict, scenario_name: str) -> Dict:
        """Compare detected results with expected results"""
        correct = True
        error_type = None
        details = {}
        
        for section_name in expected:
            expected_empty = expected[section_name]['is_empty']
            detected_empty = detected.get(section_name, {}).get('is_empty', False)
            
            details[section_name] = {
                'expected': expected_empty,
                'detected': detected_empty,
                'match': expected_empty == detected_empty
            }
            
            if expected_empty != detected_empty:
                correct = False
                if detected_empty and not expected_empty:
                    error_type = 'false_positive'
                else:
                    error_type = 'false_negative'
        
        return {
            'scenario': scenario_name,
            'correct': correct,
            'type': error_type,
            'details': details
        }
    
    def benchmark_performance(self, num_frames: int = 100) -> Dict:
        """Benchmark system performance"""
        demo_gen = DemoGenerator()
        sections = self.system.shelf_detector.get_configured_sections()
        
        # Generate test frames
        test_frames = []
        for _ in range(num_frames):
            frame = demo_gen.create_sample_shelf_image(sections, "random")
            test_frames.append(frame)
        
        # Measure processing time
        start_time = time.time()
        
        for frame in test_frames:
            self.system.process_frame(frame)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_frame = total_time / num_frames
        fps = 1.0 / avg_time_per_frame if avg_time_per_frame > 0 else 0
        
        return {
            'total_frames': num_frames,
            'total_time': total_time,
            'avg_time_per_frame': avg_time_per_frame,
            'estimated_fps': fps,
            'real_time_capable': fps >= 15  # Can handle real-time at 15+ FPS
        }

def run_demo():
    """Run a complete demo of the system"""
    from main import ShelfMonitoringSystem
    
    print("=== Shelf Monitoring System Demo ===\n")
    
    # Initialize system
    try:
        system = ShelfMonitoringSystem()
        print("✓ System initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize system: {e}")
        return
    
    # Create demo generator
    demo_gen = DemoGenerator()
    sections = system.shelf_detector.get_configured_sections()
    
    print(f"✓ Configured sections: {[s['name'] for s in sections]}")
    
    # Generate test scenarios
    scenarios = ["empty", "full", "mixed", "random"]
    
    print("\n=== Testing Different Scenarios ===")
    
    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario}")
        
        # Generate test image
        test_image = demo_gen.create_sample_shelf_image(sections, scenario)
        
        # Process image
        results = system.process_frame(test_image)
        
        # Display results
        for section_name, result in results.items():
            status = "EMPTY" if result['is_empty'] else "STOCKED"
            confidence = result['confidence']
            print(f"  {section_name}: {status} (confidence: {confidence:.1%})")
        
        # Save test image
        filename = f"demo_{scenario}.jpg"
        cv2.imwrite(filename, test_image)
        print(f"  Saved test image: {filename}")
    
    # Performance test
    print("\n=== Performance Testing ===")
    tester = PerformanceTester(system)
    
    perf_results = tester.benchmark_performance(50)
    print(f"  Processed {perf_results['total_frames']} frames in {perf_results['total_time']:.2f} seconds")
    print(f"  Average processing time: {perf_results['avg_time_per_frame']*1000:.1f}ms per frame")
    print(f"  Estimated FPS: {perf_results['estimated_fps']:.1f}")
    print(f"  Real-time capable: {'Yes' if perf_results['real_time_capable'] else 'No'}")
    
    print("\n=== Demo Complete ===")
    print("Check the generated demo images to see the system in action!")

if __name__ == "__main__":
    run_demo()
