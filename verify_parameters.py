"""
Quick Detection Parameter Verification
Verifies that our balanced parameters are properly loaded
"""
import os

# Apply OpenMP fix
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from yolo8m_shelf_detector import YOLOv8mShelfDetector
import pprint

def verify_parameters():
    """Quick verification of detection parameters"""
    print("🔧 Verifying Balanced Detection Parameters")
    print("=" * 45)
    
    try:
        # Initialize detector
        detector = YOLOv8mShelfDetector(sensitivity=0.7)
        
        # Check detection parameters
        params = detector.detection_params
        
        print("📋 Current Detection Parameters:")
        for key, value in params.items():
            print(f"   {key}: {value}")
        
        # Verify key balanced parameters
        expected_params = {
            'min_object_area': 250,
            'yolo_confidence_threshold': 0.22,
            'uniformity_threshold': 0.78,
            'yolo_low_coverage': 0.08
        }
        
        print("\n✅ Parameter Validation:")
        all_correct = True
        for param, expected in expected_params.items():
            actual = params.get(param)
            is_correct = actual == expected
            status = "✅" if is_correct else "❌"
            print(f"   {status} {param}: {actual} (expected: {expected})")
            if not is_correct:
                all_correct = False
        
        print(f"\n🎯 Parameters Status: {'✅ ALL CORRECT' if all_correct else '❌ NEEDS FIXING'}")
        
        if all_correct:
            print("\n💡 Balanced detection parameters are properly configured!")
            print("🚀 System should now accurately detect both empty and filled shelves")
        else:
            print("\n⚠️ Some parameters need adjustment")
            
        return all_correct
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_parameters()
    print("\n" + "=" * 45)
    
    if success:
        print("🎉 VERIFICATION PASSED!")
        print("✅ Ready to test with: python modern_gui.py")
    else:
        print("❌ VERIFICATION FAILED!")
        print("🔧 Parameters need manual verification")
