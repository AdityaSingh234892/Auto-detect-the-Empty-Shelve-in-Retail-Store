"""
Enhanced Empty Shelf Detection Test
Tests the improved sensitivity for empty shelf detection
"""
import os

# Apply OpenMP fix
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import numpy as np
from yolo8m_shelf_detector import YOLOv8mShelfDetector

def create_empty_shelf_test_scenarios():
    """Create various empty shelf scenarios for testing"""
    
    # 1. VERY EMPTY shelf - should definitely detect as EMPTY
    very_empty = np.ones((200, 400, 3), dtype=np.uint8) * 240  # Very light background
    # Add minimal shelf structure
    cv2.rectangle(very_empty, (10, 10), (390, 20), (220, 220, 220), -1)  # Top edge
    cv2.rectangle(very_empty, (10, 180), (390, 190), (220, 220, 220), -1)  # Bottom edge
    
    # 2. SLIGHTLY TEXTURED empty shelf - should detect as EMPTY
    textured_empty = np.ones((200, 400, 3), dtype=np.uint8) * 235
    # Add shelf structure
    cv2.rectangle(textured_empty, (10, 10), (390, 20), (210, 210, 210), -1)
    cv2.rectangle(textured_empty, (10, 180), (390, 190), (210, 210, 210), -1)
    # Add subtle texture noise
    noise = np.random.randint(-8, 8, textured_empty.shape, dtype=np.int8)
    textured_empty = cv2.add(textured_empty, noise.astype(np.uint8))
    
    # 3. EMPTY with shadows - should detect as EMPTY
    shadowed_empty = np.ones((200, 400, 3), dtype=np.uint8) * 230
    cv2.rectangle(shadowed_empty, (10, 10), (390, 20), (200, 200, 200), -1)
    cv2.rectangle(shadowed_empty, (10, 180), (390, 190), (200, 200, 200), -1)
    # Add shadow gradient
    for y in range(50, 150):
        shadow_intensity = int(230 - (y - 50) * 0.3)
        cv2.line(shadowed_empty, (0, y), (400, y), (shadow_intensity, shadow_intensity, shadow_intensity), 1)
    
    # 4. EMPTY with lighting variations - should detect as EMPTY
    lighting_empty = np.ones((200, 400, 3), dtype=np.uint8) * 225
    cv2.rectangle(lighting_empty, (10, 10), (390, 20), (195, 195, 195), -1)
    cv2.rectangle(lighting_empty, (10, 180), (390, 190), (195, 195, 195), -1)
    # Add lighting gradient
    for x in range(400):
        brightness = int(225 + 20 * np.sin(x * np.pi / 200))
        cv2.line(lighting_empty, (x, 30), (x, 170), (brightness, brightness, brightness), 1)
    
    # 5. EMPTY with shelf label - should detect as EMPTY
    labeled_empty = np.ones((200, 400, 3), dtype=np.uint8) * 238
    cv2.rectangle(labeled_empty, (10, 10), (390, 20), (215, 215, 215), -1)
    cv2.rectangle(labeled_empty, (10, 180), (390, 190), (215, 215, 215), -1)
    # Add small price label (should not affect empty detection)
    cv2.rectangle(labeled_empty, (50, 40), (120, 60), (255, 255, 255), -1)
    cv2.putText(labeled_empty, "$2.99", (55, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    return {
        'very_empty': very_empty,
        'textured_empty': textured_empty,
        'shadowed_empty': shadowed_empty,
        'lighting_empty': lighting_empty,
        'labeled_empty': labeled_empty
    }

def test_empty_shelf_detection():
    """Test enhanced empty shelf detection"""
    print("🎯 Testing Enhanced Empty Shelf Detection")
    print("=" * 50)
    
    try:
        # Initialize detector
        print("🔧 Initializing enhanced detector...")
        detector = YOLOv8mShelfDetector(sensitivity=0.8)  # Higher sensitivity for testing
        print("✅ Detector initialized with enhanced parameters")
        
        # Create test scenarios
        print("\n📸 Creating empty shelf test scenarios...")
        test_scenarios = create_empty_shelf_test_scenarios()
        print("✅ Test scenarios created")
        
        print(f"\n🔍 Enhanced Detection Parameters:")
        params = detector.detection_params
        print(f"   • min_object_area: {params['min_object_area']}")
        print(f"   • uniformity_threshold: {params['uniformity_threshold']}")
        print(f"   • yolo_confidence_threshold: {params['yolo_confidence_threshold']}")
        print(f"   • empty_confidence_boost: {params['empty_confidence_boost']}")
        
        # Test each scenario
        print("\n🔍 Testing Empty Shelf Detection...")
        results = {}
        
        for scenario, image in test_scenarios.items():
            print(f"\n   📋 Testing: {scenario.replace('_', ' ').title()}")
            
            result = detector.analyze_shelf_region(image, f"test_{scenario}")
            
            is_empty = result['is_empty']
            confidence = result['confidence']
            visual_state = result['visual_state']
            should_alert = result['should_alert']
            
            results[scenario] = {
                'is_empty': is_empty,
                'confidence': confidence,
                'visual_state': visual_state,
                'should_alert': should_alert
            }
            
            # All scenarios should detect as EMPTY
            status = "✅ CORRECT" if is_empty else "❌ MISSED EMPTY SHELF"
            alert_status = "🚨 ALERT" if should_alert else "🔕 NO ALERT"
            
            print(f"      Result: {'EMPTY' if is_empty else 'FILLED'}")
            print(f"      Confidence: {confidence:.1%}")
            print(f"      Visual State: {visual_state}")
            print(f"      Status: {status}")
            print(f"      Alert: {alert_status}")
            
            if not is_empty:
                print(f"      ⚠️  ERROR: This should be detected as EMPTY!")
        
        # Calculate success rate
        print("\n" + "=" * 50)
        print("📊 EMPTY SHELF DETECTION RESULTS:")
        
        successful_detections = sum(1 for r in results.values() if r['is_empty'])
        total_tests = len(results)
        success_rate = (successful_detections / total_tests) * 100
        
        print(f"\n   Empty Shelf Detection Rate: {successful_detections}/{total_tests} ({success_rate:.1f}%)")
        
        # Show detailed results
        print("\n   Detailed Results:")
        for scenario, result in results.items():
            scenario_name = scenario.replace('_', ' ').title()
            status_icon = "✅" if result['is_empty'] else "❌"
            alert_icon = "🚨" if result['should_alert'] else "🔕"
            
            print(f"   {status_icon} {scenario_name:18} - "
                  f"{'Empty' if result['is_empty'] else 'Filled':6} | "
                  f"Confidence: {result['confidence']:>5.1%} | "
                  f"{alert_icon}")
        
        if success_rate >= 80:
            print(f"\n🎉 EXCELLENT! Empty detection working: {success_rate:.1f}%")
            print("   ✅ Enhanced parameters successfully improved empty shelf detection")
        elif success_rate >= 60:
            print(f"\n⚠️ GOOD but could be better: {success_rate:.1f}%")
            print("   🔧 Consider increasing sensitivity further")
        else:
            print(f"\n❌ POOR detection rate: {success_rate:.1f}%")
            print("   🔧 Parameters need more adjustment")
            
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_empty_shelf_detection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 EMPTY SHELF DETECTION IMPROVED!")
        print("\n💡 Your system should now:")
        print("   ✅ Detect empty shelves more reliably")
        print("   ✅ Trigger alerts at 65% confidence (reduced threshold)")
        print("   ✅ Handle various lighting and texture conditions")
        print("   ✅ Be more sensitive to truly empty shelves")
        print("\n🚀 Ready for video testing: python modern_gui.py")
    else:
        print("⚠️ EMPTY DETECTION STILL NEEDS WORK")
        print("🔧 Consider manually adjusting sensitivity in the GUI")
        print("💡 Try setting sensitivity to 0.8 or 0.9 for maximum detection")
    
    print("\n📋 Troubleshooting Tips:")
    print("1. Use higher sensitivity (0.8-0.9) in the GUI")
    print("2. Ensure proper lighting in your video")
    print("3. Check that shelf regions are clearly visible")
    print("4. Verify video quality is sufficient for detection")
