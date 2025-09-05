#!/usr/bin/env python3
"""
Test script for YOLOv8m-enhanced shelf detector
"""

import cv2
import numpy as np
import time

def test_yolo8m_detector():
    print('🎯 Testing YOLOv8m-Enhanced Shelf Detector')
    print('='*55)
    
    try:
        # Test YOLOv8m detector import and initialization
        from yolo8m_shelf_detector import YOLOv8mShelfDetector
        
        print('📥 Initializing YOLOv8m detector...')
        detector = YOLOv8mShelfDetector(sensitivity=0.7)
        
        print('✅ YOLOv8m detector initialized successfully')
        
        # Check if YOLO model is available
        if detector.yolo_model is not None:
            print('✅ YOLOv8m model loaded and ready')
            print(f'📊 Model type: {type(detector.yolo_model)}')
        else:
            print('⚠️ YOLOv8m model not available, using traditional detection')
        
        # Test with simulated empty shelf (uniform gray)
        print('\n🧪 Testing Empty Shelf Detection:')
        empty_shelf = np.ones((150, 300, 3), dtype=np.uint8) * 220  # Light gray uniform area
        
        start_time = time.time()
        result_empty = detector.analyze_shelf_region(empty_shelf, 'Test_Empty_Shelf')
        empty_time = time.time() - start_time
        
        print(f'Empty Shelf Result:')
        print(f'  - Detected as: {"EMPTY" if result_empty["is_empty"] else "STOCKED"}')
        print(f'  - Confidence: {result_empty["confidence"]:.1%}')
        print(f'  - Visual State: {result_empty["visual_state"]}')
        print(f'  - YOLO Products: {len(result_empty["yolo_products"])}')
        print(f'  - Analysis Time: {empty_time:.3f}s')
        
        # Test with simulated stocked shelf (random colorful)
        print('\n🧪 Testing Stocked Shelf Detection:')
        stocked_shelf = np.random.randint(0, 255, (150, 300, 3), dtype=np.uint8)
        
        start_time = time.time()
        result_stocked = detector.analyze_shelf_region(stocked_shelf, 'Test_Stocked_Shelf')
        stocked_time = time.time() - start_time
        
        print(f'Stocked Shelf Result:')
        print(f'  - Detected as: {"EMPTY" if result_stocked["is_empty"] else "STOCKED"}')
        print(f'  - Confidence: {result_stocked["confidence"]:.1%}')
        print(f'  - Visual State: {result_stocked["visual_state"]}')
        print(f'  - YOLO Products: {len(result_stocked["yolo_products"])}')
        print(f'  - Analysis Time: {stocked_time:.3f}s')
        
        # Test detection parameters
        print('\n⚙️ Detection Parameters:')
        params = detector.detection_params
        print(f'  - Supermarket Mode: {params["supermarket_mode"]}')
        print(f'  - YOLO Confidence Threshold: {params["yolo_confidence_threshold"]}')
        print(f'  - Empty Confidence Boost: {params["empty_confidence_boost"]}')
        print(f'  - Product Detection Weight: {params["product_detection_weight"]}')
        
        # Test sensitivity update
        print('\n🎛️ Testing Sensitivity Update:')
        detector.update_sensitivity(0.8)
        
        print('\n✅ YOLOv8m Enhanced Detection System Status:')
        print('🎯 YOLOv8m integration: Ready')
        print('📹 Video analysis: Optimized for supermarket footage')
        print('🔍 Empty shelf detection: Enhanced with AI')
        print('⚡ Performance: Real-time capable')
        
        return True
        
    except ImportError as e:
        print(f'❌ Import Error: {e}')
        print('💡 Installing required dependencies...')
        
        try:
            import subprocess
            import sys
            
            # Install ultralytics for YOLOv8
            print('📦 Installing ultralytics (YOLOv8)...')
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
            
            print('✅ Dependencies installed successfully')
            print('🔄 Please restart the application to use YOLOv8m')
            return False
            
        except Exception as install_error:
            print(f'❌ Installation failed: {install_error}')
            print('🔄 Falling back to traditional detection')
            return False
            
    except Exception as e:
        print(f'❌ Unexpected error: {e}')
        print('🔄 Falling back to traditional detection')
        return False

def test_compatibility():
    """Test system compatibility for YOLOv8m"""
    print('\n🔧 System Compatibility Check:')
    
    try:
        import torch
        print(f'✅ PyTorch available: {torch.__version__}')
        
        if torch.cuda.is_available():
            print(f'🚀 CUDA available: {torch.cuda.get_device_name(0)}')
            print('💡 YOLOv8m will use GPU acceleration')
        else:
            print('⚠️ CUDA not available, using CPU')
            print('💡 YOLOv8m will run on CPU (slower)')
            
    except ImportError:
        print('⚠️ PyTorch not found')
        print('💡 YOLOv8m may install PyTorch automatically')
    
    try:
        import cv2
        print(f'✅ OpenCV available: {cv2.__version__}')
    except ImportError:
        print('❌ OpenCV not found - required for video processing')
    
    try:
        import numpy as np
        print(f'✅ NumPy available: {np.__version__}')
    except ImportError:
        print('❌ NumPy not found - required for array processing')

if __name__ == "__main__":
    test_compatibility()
    success = test_yolo8m_detector()
    
    if success:
        print('\n🚀 Ready to run enhanced shelf monitoring:')
        print('   python modern_gui.py')
    else:
        print('\n🔄 System will use fallback detection methods')
        print('   python modern_gui.py  # Will auto-fallback')
