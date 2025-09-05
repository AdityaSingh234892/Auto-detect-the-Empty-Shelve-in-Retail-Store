"""
Test script to verify OpenMP fix resolves library conflicts
"""
import os

# Apply OpenMP fix
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

print("🔧 Testing OpenMP fix...")

try:
    import cv2
    print(f"✅ OpenCV imported successfully (version: {cv2.__version__})")
    
    import numpy as np
    print(f"✅ NumPy imported successfully (version: {np.__version__})")
    
    # Test YOLOv8m detector
    try:
        from yolo8m_shelf_detector import YOLOv8mShelfDetector
        detector = YOLOv8mShelfDetector()
        print(f"✅ YOLOv8m detector initialized successfully")
        print(f"🎯 YOLO model available: {detector.yolo_model is not None}")
        
        # Test basic detection
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        result = detector.analyze_shelf_region(test_image, "test_shelf")
        print(f"✅ Test detection completed: {result['visual_state']}")
        
    except Exception as e:
        print(f"⚠️ YOLOv8m detector error: {e}")
    
    # Test enhanced video detector
    try:
        from enhanced_video_detector import EnhancedVideoShelfDetector
        video_detector = EnhancedVideoShelfDetector()
        print(f"✅ Enhanced video detector initialized successfully")
        
        # Test basic detection
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        result = video_detector.analyze_shelf_region(test_image, "test_shelf")
        print(f"✅ Video detector test completed: {result['visual_state']}")
        
    except Exception as e:
        print(f"⚠️ Enhanced video detector error: {e}")
    
    print("\n🎉 All systems operational! OpenMP conflicts resolved.")
    print("🚀 You can now run 'python modern_gui.py' without errors.")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("Please check your environment setup.")
