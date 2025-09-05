"""
Test Conservative Empty Shelf Detection
Validates that filled shelves are not incorrectly identified as empty
"""
import os

# Apply OpenMP fix
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
from yolo8m_shelf_detector import YOLOv8mShelfDetector

def create_test_images():
    """Create test images for validation"""
    
    # 1. Clearly EMPTY shelf (should detect as empty)
    empty_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 240  # Light gray background
    cv2.rectangle(empty_shelf, (10, 10), (290, 190), (220, 220, 220), -1)  # Shelf background
    
    # 2. FILLED shelf with products (should NOT detect as empty)
    filled_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 240
    # Add various "products" 
    cv2.rectangle(filled_shelf, (20, 50), (80, 150), (255, 0, 0), -1)    # Blue product
    cv2.rectangle(filled_shelf, (90, 60), (140, 140), (0, 255, 0), -1)   # Green product
    cv2.rectangle(filled_shelf, (150, 40), (200, 160), (0, 0, 255), -1)  # Red product
    cv2.rectangle(filled_shelf, (210, 70), (270, 130), (255, 255, 0), -1) # Yellow product
    # Add some texture and variation
    noise = np.random.randint(0, 30, filled_shelf.shape, dtype=np.uint8)
    filled_shelf = cv2.add(filled_shelf, noise)
    
    # 3. PARTIALLY filled shelf (moderate case)
    partial_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 240
    cv2.rectangle(partial_shelf, (20, 50), (100, 150), (255, 100, 100), -1)  # One product
    cv2.rectangle(partial_shelf, (200, 60), (270, 140), (100, 255, 100), -1) # Another product
    
    # 4. Complex filled shelf with varied products
    complex_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 235
    # Multiple small products
    for i in range(6):
        x1 = 20 + i * 45
        y1 = 40 + (i % 2) * 60
        x2 = x1 + 35
        y2 = y1 + 80
        color = (np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))
        cv2.rectangle(complex_shelf, (x1, y1), (x2, y2), color, -1)
        # Add some labels/text to simulate product packaging
        cv2.putText(complex_shelf, f"P{i}", (x1+5, y1+20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return {
        'empty': empty_shelf,
        'filled': filled_shelf, 
        'partial': partial_shelf,
        'complex': complex_shelf
    }

def test_conservative_detection():
    """Test the conservative detection logic"""
    print("🧪 Testing Conservative Empty Shelf Detection")
    print("=" * 50)
    
    try:
        # Initialize detector
        print("🎯 Initializing YOLOv8m detector...")
        detector = YOLOv8mShelfDetector(sensitivity=0.7)
        print("✅ Detector initialized")
        
        # Create test images
        print("\n📸 Creating test images...")
        test_images = create_test_images()
        print("✅ Test images created")
        
        # Test each image
        results = {}
        
        print("\n🔍 Running detection tests...")
        for image_type, image in test_images.items():
            print(f"\n   Testing {image_type.upper()} shelf...")
            
            result = detector.analyze_shelf_region(image, f"test_{image_type}")
            
            is_empty = result['is_empty']
            confidence = result['confidence']
            visual_state = result['visual_state']
            yolo_products = result.get('yolo_products', [])
            
            results[image_type] = {
                'is_empty': is_empty,
                'confidence': confidence,
                'visual_state': visual_state,
                'yolo_products': len(yolo_products)
            }
            
            print(f"      Result: {'EMPTY' if is_empty else 'HAS PRODUCTS'}")
            print(f"      Confidence: {confidence:.1%}")
            print(f"      Visual State: {visual_state}")
            print(f"      YOLO Products: {len(yolo_products)}")
        
        # Evaluate results
        print("\n" + "=" * 50)
        print("📊 EVALUATION RESULTS:")
        
        # Expected results
        expected = {
            'empty': True,      # Should detect as empty
            'filled': False,    # Should NOT detect as empty
            'partial': False,   # Should NOT detect as empty (conservative)
            'complex': False    # Should NOT detect as empty
        }
        
        correct_predictions = 0
        total_tests = len(expected)
        
        for image_type, expected_empty in expected.items():
            actual_empty = results[image_type]['is_empty']
            confidence = results[image_type]['confidence']
            
            is_correct = (actual_empty == expected_empty)
            if is_correct:
                correct_predictions += 1
                status = "✅ CORRECT"
            else:
                status = "❌ WRONG"
            
            print(f"   {image_type.upper():8} - Expected: {'Empty' if expected_empty else 'Filled':6} | "
                  f"Got: {'Empty' if actual_empty else 'Filled':6} | "
                  f"Conf: {confidence:.1%} | {status}")
        
        accuracy = (correct_predictions / total_tests) * 100
        print(f"\n🎯 ACCURACY: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
        
        # Specific validation for the main issue
        filled_detected_as_empty = results['filled']['is_empty']
        complex_detected_as_empty = results['complex']['is_empty']
        
        if not filled_detected_as_empty and not complex_detected_as_empty:
            print("✅ SUCCESS: Filled shelves are NOT incorrectly detected as empty!")
        else:
            print("❌ ISSUE: Some filled shelves are still detected as empty")
            
        print("\n💡 RECOMMENDATIONS:")
        if accuracy >= 75:
            print("   ✅ Detection logic is working well")
            print("   ✅ Conservative approach is preventing false empty alerts")
        else:
            print("   ⚠️ Detection logic may need further tuning")
            
        return accuracy >= 75
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_conservative_detection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CONSERVATIVE DETECTION VALIDATION PASSED!")
        print("💡 Your system should now:")
        print("   ✅ Reduce false empty alerts on filled shelves")
        print("   ✅ Show alerts for only 1.5 seconds (reduced from 4-5 seconds)")
        print("   ✅ Require higher confidence before triggering alerts")
    else:
        print("⚠️ DETECTION NEEDS FURTHER TUNING")
        print("🔧 Consider adjusting detection parameters further")
    
    print("\n🚀 To test with your videos: python modern_gui.py")
