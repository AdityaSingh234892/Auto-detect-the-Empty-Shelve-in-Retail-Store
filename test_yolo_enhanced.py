"""
Test script for the enhanced YOLO shelf detection system
This script demonstrates the improved accuracy and visual feedback
"""
import cv2
import numpy as np
import time
from yolo_enhanced_detector import YOLOShelfDetector

def create_test_images():
    """Create test images to demonstrate detection capabilities"""
    
    # Test image 1: Truly empty shelf (minimal variation, uniform background)
    empty_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 245  # Very light, uniform
    # Add minimal shelf structure only
    cv2.line(empty_shelf, (0, 180), (300, 180), (235, 235, 235), 1)  # Bottom edge
    cv2.line(empty_shelf, (0, 20), (300, 20), (235, 235, 235), 1)   # Top edge
    cv2.line(empty_shelf, (20, 20), (20, 180), (235, 235, 235), 1)  # Left edge
    cv2.line(empty_shelf, (280, 20), (280, 180), (235, 235, 235), 1) # Right edge
    # Very minimal noise to simulate real shelf
    noise = np.random.normal(0, 2, empty_shelf.shape).astype(np.uint8)
    empty_shelf = cv2.add(empty_shelf, noise)
    
    # Test image 2: Fully stocked shelf (high variation, multiple objects)
    stocked_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 180
    # Add many colorful products with varied shapes and sizes
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
              (255, 0, 255), (0, 255, 255), (128, 255, 0), (255, 128, 0)]
    
    for i in range(8):
        x = 20 + (i % 4) * 65
        y = 30 + (i // 4) * 80
        w = 45 + np.random.randint(-5, 15)
        h = 70 + np.random.randint(-10, 20)
        color = colors[i % len(colors)]
        
        # Draw product with texture
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), color, -1)
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), (0, 0, 0), 2)
        
        # Add text labels and details
        cv2.putText(stocked_shelf, f"ITEM", (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        cv2.putText(stocked_shelf, f"{i+1}", (x+5, y+35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Add some texture patterns
        for j in range(3):
            cv2.line(stocked_shelf, (x+10, y+45+j*8), (x+w-10, y+45+j*8), (255, 255, 255), 1)
    
    # Test image 3: Partially empty shelf (some products, clear empty space)
    partial_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 240  # Light background
    
    # Add shelf structure
    cv2.line(partial_shelf, (0, 180), (300, 180), (220, 220, 220), 2)
    cv2.line(partial_shelf, (150, 20), (150, 180), (230, 230, 230), 1)  # Divider
    
    # Add only 2-3 products on one side
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i in range(3):
        x = 20 + i * 40
        y = 50
        color = colors[i]
        cv2.rectangle(partial_shelf, (x, y), (x + 35, y + 80), color, -1)
        cv2.rectangle(partial_shelf, (x, y), (x + 35, y + 80), (0, 0, 0), 2)
        cv2.putText(partial_shelf, f"P{i+1}", (x+8, y+45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Leave right side clearly empty with minimal variation
    empty_area = partial_shelf[20:180, 160:290]
    empty_area[:] = 245  # Very uniform empty area
    
    # Test image 4: Almost empty shelf (just one small item)
    almost_empty = np.ones((200, 300, 3), dtype=np.uint8) * 248
    # Minimal shelf structure
    cv2.line(almost_empty, (0, 180), (300, 180), (240, 240, 240), 1)
    # One tiny item
    cv2.rectangle(almost_empty, (50, 120), (80, 160), (100, 100, 255), -1)
    cv2.rectangle(almost_empty, (50, 120), (80, 160), (0, 0, 0), 1)
    
    return {
        'empty': empty_shelf,
        'stocked': stocked_shelf,
        'partial': partial_shelf,
        'almost_empty': almost_empty
    }

def test_yolo_detection():
    """Test the YOLO-enhanced detection system"""
    print("🎯 Testing YOLO-Enhanced Shelf Detection System")
    print("=" * 50)
    
    # Initialize detector
    detector = YOLOShelfDetector(sensitivity=0.7)
    
    # Create test images
    test_images = create_test_images()
    
    # Test each image
    for image_name, image in test_images.items():
        print(f"\n📊 Testing {image_name.upper()} shelf:")
        print("-" * 30)
        
        # Analyze the image
        result = detector.analyze_shelf_region(image, f"Test_{image_name}", time.time())
        
        # Display comprehensive results
        print(f"🔍 Detection Results:")
        print(f"   Empty Status: {'❌ EMPTY' if result['is_empty'] else '✅ STOCKED'}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Fullness Score: {result['fullness_score']:.1%}")
        print(f"   Visual State: {result['visual_state']}")
        print(f"   Alert Level: {result['alert_level']}")
        print(f"   Should Alert: {'🚨 YES' if result['should_alert'] else '🔕 NO'}")
        print(f"   Trend: {result['trend']}")
        print(f"   Detection Strength: {result['detection_strength']:.2f}")
        
        print(f"\n🎯 Method Breakdown:")
        method_scores = result['method_scores']
        for method, score in method_scores.items():
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {method.replace('_', ' ').title():20}: {bar} {score:.2f}")
        
        print(f"\n📈 Analysis Details:")
        details = result['details']
        if 'object_features' in details:
            obj_features = details['object_features']
            print(f"   Objects Detected: {obj_features['object_count']}")
            print(f"   Coverage Ratio: {obj_features['coverage_ratio']:.2%}")
            print(f"   Density Score: {obj_features['density_score']:.2f}")
        
        if 'color_analysis' in details:
            color_analysis = details['color_analysis']
            print(f"   Color Diversity: {color_analysis['color_diversity']:.1f}")
            print(f"   Color Peaks: {color_analysis['color_peaks']}")
        
        if 'texture_analysis' in details:
            texture = details['texture_analysis']
            print(f"   Texture Strength: {texture['texture_strength']:.1f}")
            print(f"   Pattern Complexity: {texture['pattern_complexity']:.1f}")
        
        print(f"\n📱 Visual Feedback:")
        visual_feedback = result['visual_feedback']
        print(f"   Color: {visual_feedback['color']}")
        print(f"   Thickness: {visual_feedback['thickness']}")
        print(f"   Should Pulse: {'⚡ YES' if visual_feedback['should_pulse'] else '🔸 NO'}")
        print(f"   Alert Duration: {visual_feedback['alert_duration']}ms")
        print(f"   Play Sound: {'🔊 YES' if visual_feedback['play_sound'] else '🔇 NO'}")
        
        # Save test image with overlay
        display_image = image.copy()
        
        # Add detection result overlay
        state_color = visual_feedback['color']
        thickness = visual_feedback['thickness']
        
        # Draw border based on detection
        cv2.rectangle(display_image, (5, 5), (image.shape[1]-5, image.shape[0]-5), 
                     state_color, thickness)
        
        # Add text overlay
        cv2.putText(display_image, f"{result['visual_state']}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, state_color, 2)
        cv2.putText(display_image, f"Conf: {result['confidence']:.1%}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        cv2.putText(display_image, f"Full: {result['fullness_score']:.1%}", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        
        # Save the result
        filename = f"test_{image_name}_result.jpg"
        cv2.imwrite(filename, display_image)
        print(f"💾 Saved result image: {filename}")
    
    print(f"\n🎉 YOLO-Enhanced Detection Test Complete!")
    print("Key improvements:")
    print("✅ Multi-stage analysis (objects, color, texture, spatial, structure)")
    print("✅ YOLO-inspired confidence scoring")
    print("✅ Enhanced visual feedback with pulsing alerts")
    print("✅ Comprehensive method scoring")
    print("✅ Trend analysis and stability metrics")
    print("✅ Rich alert configuration with priorities")

def test_sensitivity_adjustment():
    """Test sensitivity adjustment feature"""
    print(f"\n🎛️ Testing Sensitivity Adjustment")
    print("=" * 40)
    
    detector = YOLOShelfDetector()
    test_images = create_test_images()
    
    # Test with different sensitivity levels
    sensitivities = [0.3, 0.5, 0.7, 0.9]
    
    for sensitivity in sensitivities:
        print(f"\n📊 Sensitivity: {sensitivity}")
        detector.update_sensitivity(sensitivity)
        
        result = detector.analyze_shelf_region(test_images['partial'], "Partial_Test", time.time())
        print(f"   Empty Status: {'❌' if result['is_empty'] else '✅'} | "
              f"Confidence: {result['confidence']:.1%} | "
              f"Fullness: {result['fullness_score']:.1%}")

if __name__ == "__main__":
    # Run comprehensive tests
    test_yolo_detection()
    test_sensitivity_adjustment()
    
    print(f"\n🚀 Ready to integrate with modern_gui_fixed.py!")
    print("The enhanced YOLO detection system provides:")
    print("• Better empty shelf identification accuracy")
    print("• Rich visual feedback with confidence percentages")
    print("• Multi-method analysis scoring")
    print("• Real-time detection status displays")
    print("• Enhanced alert system with priorities")
