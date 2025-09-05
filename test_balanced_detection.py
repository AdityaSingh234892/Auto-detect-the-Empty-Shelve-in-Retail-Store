"""
Balanced Detection Accuracy Test
Tests both empty and filled shelf detection with realistic scenarios
"""
import os

# Apply OpenMP fix
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
from yolo8m_shelf_detector import YOLOv8mShelfDetector

def create_realistic_test_images():
    """Create realistic test images for validation"""
    
    # 1. CLEARLY EMPTY shelf - should detect as EMPTY
    empty_shelf = np.ones((200, 400, 3), dtype=np.uint8) * 235  # Light background
    # Add shelf structure but no products
    cv2.rectangle(empty_shelf, (10, 10), (390, 30), (200, 200, 200), -1)  # Top shelf edge
    cv2.rectangle(empty_shelf, (10, 170), (390, 190), (200, 200, 200), -1)  # Bottom shelf edge
    cv2.line(empty_shelf, (0, 100), (400, 100), (210, 210, 210), 2)  # Shelf divider
    # Add very subtle noise to make it realistic
    noise = np.random.randint(-5, 5, empty_shelf.shape, dtype=np.int8)
    empty_shelf = cv2.add(empty_shelf, noise.astype(np.uint8))
    
    # 2. CLEARLY FILLED shelf - should detect as FILLED
    filled_shelf = np.ones((200, 400, 3), dtype=np.uint8) * 230
    # Add shelf structure
    cv2.rectangle(filled_shelf, (10, 10), (390, 30), (200, 200, 200), -1)
    cv2.rectangle(filled_shelf, (10, 170), (390, 190), (200, 200, 200), -1)
    # Add multiple distinct products
    products = [
        {'pos': (30, 50), 'size': (60, 100), 'color': (255, 100, 100)},   # Red product
        {'pos': (110, 60), 'size': (50, 90), 'color': (100, 255, 100)},   # Green product
        {'pos': (180, 45), 'size': (70, 110), 'color': (100, 100, 255)},  # Blue product
        {'pos': (270, 55), 'size': (55, 95), 'color': (255, 255, 100)},   # Yellow product
        {'pos': (340, 50), 'size': (45, 105), 'color': (255, 100, 255)},  # Magenta product
    ]
    for product in products:
        x, y = product['pos']
        w, h = product['size']
        color = product['color']
        cv2.rectangle(filled_shelf, (x, y), (x+w, y+h), color, -1)
        # Add product labels/texture
        cv2.putText(filled_shelf, "PROD", (x+5, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        # Add some texture variation
        texture_noise = np.random.randint(-10, 10, (h, w, 3), dtype=np.int8)
        shelf_region = filled_shelf[y:y+h, x:x+w]
        filled_shelf[y:y+h, x:x+w] = cv2.add(shelf_region, texture_noise.astype(np.uint8))
    
    # 3. MOSTLY EMPTY shelf - should detect as EMPTY
    mostly_empty = np.ones((200, 400, 3), dtype=np.uint8) * 238
    cv2.rectangle(mostly_empty, (10, 10), (390, 30), (200, 200, 200), -1)
    cv2.rectangle(mostly_empty, (10, 170), (390, 190), (200, 200, 200), -1)
    # Add just one small product in corner
    cv2.rectangle(mostly_empty, (320, 140), (370, 165), (150, 150, 255), -1)
    cv2.putText(mostly_empty, "P", (335, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    # 4. SPARSELY FILLED shelf - should detect as FILLED (has products)
    sparse_shelf = np.ones((200, 400, 3), dtype=np.uint8) * 232
    cv2.rectangle(sparse_shelf, (10, 10), (390, 30), (200, 200, 200), -1)
    cv2.rectangle(sparse_shelf, (10, 170), (390, 190), (200, 200, 200), -1)
    # Add 3 products with gaps
    cv2.rectangle(sparse_shelf, (50, 60), (100, 140), (200, 100, 100), -1)
    cv2.rectangle(sparse_shelf, (180, 70), (220, 130), (100, 200, 100), -1)
    cv2.rectangle(sparse_shelf, (300, 55), (350, 145), (100, 100, 200), -1)
    # Add labels
    for i, x in enumerate([75, 200, 325]):
        cv2.putText(sparse_shelf, f"P{i+1}", (x-10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # 5. DENSELY FILLED shelf - should detect as FILLED
    dense_shelf = np.ones((200, 400, 3), dtype=np.uint8) * 225
    cv2.rectangle(dense_shelf, (10, 10), (390, 30), (200, 200, 200), -1)
    cv2.rectangle(dense_shelf, (10, 170), (390, 190), (200, 200, 200), -1)
    # Pack with many products
    for i in range(8):
        x = 25 + i * 45
        y = 45 + (i % 2) * 20
        w, h = 35, 80 + (i % 3) * 10
        color = (50 + i * 25, 255 - i * 20, 100 + i * 15)
        cv2.rectangle(dense_shelf, (x, y), (x+w, y+h), color, -1)
        cv2.putText(dense_shelf, f"{i+1}", (x+10, y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    return {
        'clearly_empty': empty_shelf,
        'clearly_filled': filled_shelf,
        'mostly_empty': mostly_empty,
        'sparsely_filled': sparse_shelf,
        'densely_filled': dense_shelf
    }

def test_balanced_detection():
    """Test the balanced detection logic for accuracy"""
    print("🎯 Testing Balanced Empty/Filled Shelf Detection")
    print("=" * 55)
    
    try:
        # Initialize detector
        print("🔧 Initializing YOLOv8m detector...")
        detector = YOLOv8mShelfDetector(sensitivity=0.7)
        print("✅ Detector initialized with balanced parameters")
        
        # Create test images
        print("\n📸 Creating realistic test scenarios...")
        test_images = create_realistic_test_images()
        print("✅ Test scenarios created")
        
        # Expected results (what we want the system to detect)
        expected_results = {
            'clearly_empty': True,      # Should detect as EMPTY
            'clearly_filled': False,    # Should detect as FILLED (not empty)
            'mostly_empty': True,       # Should detect as EMPTY (mostly empty)
            'sparsely_filled': False,   # Should detect as FILLED (has products)
            'densely_filled': False     # Should detect as FILLED (many products)
        }
        
        # Test each scenario
        results = {}
        print("\n🔍 Running balanced detection tests...")
        
        for scenario, image in test_images.items():
            print(f"\n   📋 Testing: {scenario.replace('_', ' ').title()}")
            
            result = detector.analyze_shelf_region(image, f"test_{scenario}")
            
            is_empty = result['is_empty']
            confidence = result['confidence']
            visual_state = result['visual_state']
            yolo_products = result.get('yolo_products', [])
            method_scores = result.get('method_scores', {})
            
            results[scenario] = {
                'is_empty': is_empty,
                'confidence': confidence,
                'visual_state': visual_state,
                'yolo_products': len(yolo_products),
                'method_scores': method_scores
            }
            
            expected = expected_results[scenario]
            status = "✅ CORRECT" if (is_empty == expected) else "❌ WRONG"
            
            print(f"      Result: {'EMPTY' if is_empty else 'FILLED'}")
            print(f"      Expected: {'EMPTY' if expected else 'FILLED'}")
            print(f"      Confidence: {confidence:.1%}")
            print(f"      Visual State: {visual_state}")
            print(f"      YOLO Products: {len(yolo_products)}")
            print(f"      Status: {status}")
            
            # Show method breakdown for debugging
            if method_scores:
                print("      Method Scores:")
                for method, score in method_scores.items():
                    print(f"        {method}: {score:.2f}")
        
        # Calculate accuracy
        print("\n" + "=" * 55)
        print("📊 OVERALL ACCURACY ASSESSMENT:")
        
        correct_predictions = 0
        total_tests = len(expected_results)
        
        print("\n   Detailed Results:")
        for scenario, expected_empty in expected_results.items():
            actual_empty = results[scenario]['is_empty']
            confidence = results[scenario]['confidence']
            
            is_correct = (actual_empty == expected_empty)
            if is_correct:
                correct_predictions += 1
                
            status_icon = "✅" if is_correct else "❌"
            scenario_name = scenario.replace('_', ' ').title()
            
            print(f"   {status_icon} {scenario_name:15} - Expected: {'Empty' if expected_empty else 'Filled':6} | "
                  f"Got: {'Empty' if actual_empty else 'Filled':6} | Confidence: {confidence:.1%}")
        
        accuracy = (correct_predictions / total_tests) * 100
        print(f"\n🎯 FINAL ACCURACY: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
        
        # Specific issue validation
        empty_detection_ok = results['clearly_empty']['is_empty'] and results['mostly_empty']['is_empty']
        filled_detection_ok = (not results['clearly_filled']['is_empty'] and 
                              not results['sparsely_filled']['is_empty'] and 
                              not results['densely_filled']['is_empty'])
        
        print(f"\n🔍 ISSUE-SPECIFIC VALIDATION:")
        print(f"   Empty Shelf Detection: {'✅ WORKING' if empty_detection_ok else '❌ FAILING'}")
        print(f"   Filled Shelf Detection: {'✅ WORKING' if filled_detection_ok else '❌ FAILING'}")
        
        if accuracy >= 80:
            print(f"\n🎉 EXCELLENT! Detection accuracy is {accuracy:.1f}%")
            print("   ✅ System should now correctly identify both empty and filled shelves")
        elif accuracy >= 60:
            print(f"\n⚠️ GOOD but needs improvement. Accuracy: {accuracy:.1f}%")
            print("   🔧 Consider fine-tuning parameters further")
        else:
            print(f"\n❌ POOR accuracy: {accuracy:.1f}%")
            print("   🔧 Significant parameter adjustment needed")
            
        return accuracy >= 80
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_balanced_detection()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 BALANCED DETECTION VALIDATION PASSED!")
        print("\n💡 Your system should now correctly:")
        print("   ✅ Identify truly empty shelves as EMPTY")
        print("   ✅ Identify shelves with products as FILLED")
        print("   ✅ Handle edge cases (sparse/dense shelves) appropriately")
        print("   ✅ Show alerts for 1.5 seconds with 75% confidence threshold")
        print("\n🚀 Ready for real-world testing: python modern_gui.py")
    else:
        print("⚠️ DETECTION STILL NEEDS TUNING")
        print("🔧 The parameters may need further adjustment for your specific videos")
        print("💡 Try adjusting sensitivity in the GUI or modify detection parameters")
    
    print("\n📋 Next Steps:")
    print("1. Test with your actual supermarket videos")
    print("2. Adjust sensitivity slider if needed (0.1-0.9)")
    print("3. Monitor real-world accuracy and fine-tune as needed")
