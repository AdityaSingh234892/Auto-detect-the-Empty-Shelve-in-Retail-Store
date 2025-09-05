"""
Quick test script to verify system setup and basic functionality
"""
import sys
import importlib
import cv2
import numpy as np

def test_imports():
    """Test if all required packages are available"""
    print("Testing package imports...")
    
    required_packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('yaml', 'pyyaml'),
        ('matplotlib', 'matplotlib'),
        ('PIL', 'pillow')
    ]
    
    optional_packages = [
        ('ultralytics', 'ultralytics'),
        ('playsound', 'playsound')
    ]
    
    all_good = True
    
    # Test required packages
    for package, pip_name in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package} ({pip_name})")
        except ImportError:
            print(f"  ✗ {package} ({pip_name}) - MISSING")
            all_good = False
    
    # Test optional packages
    for package, pip_name in optional_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package} ({pip_name}) - optional")
        except ImportError:
            print(f"  ⚠ {package} ({pip_name}) - optional, not installed")
    
    return all_good

def test_opencv():
    """Test OpenCV functionality"""
    print("\nTesting OpenCV functionality...")
    
    try:
        # Create a test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = (100, 150, 200)  # Fill with color
        
        # Test basic operations
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print("  ✓ Image creation and color conversion")
        print("  ✓ Canny edge detection")
        print("  ✓ Contour detection")
        
        return True
    except Exception as e:
        print(f"  ✗ OpenCV test failed: {e}")
        return False

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("  ✓ Camera accessible and working")
                print(f"  ✓ Frame shape: {frame.shape}")
            else:
                print("  ⚠ Camera opened but failed to read frame")
            cap.release()
        else:
            print("  ⚠ Cannot open camera (might be in use or not available)")
        
        return True
    except Exception as e:
        print(f"  ✗ Camera test failed: {e}")
        return False

def test_yolo():
    """Test YOLO functionality"""
    print("\nTesting YOLO functionality...")
    
    try:
        from ultralytics import YOLO
        
        # Try to load a small YOLO model
        print("  Attempting to load YOLOv8 nano model...")
        model = YOLO('yolov8n.pt')  # This will download if not present
        print("  ✓ YOLO model loaded successfully")
        
        # Test inference on dummy image
        test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        results = model(test_image)
        print("  ✓ YOLO inference test successful")
        
        return True
    except ImportError:
        print("  ⚠ Ultralytics not installed - YOLO features will be disabled")
        return False
    except Exception as e:
        print(f"  ✗ YOLO test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        import yaml
        
        # Test config file existence
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            print("  ✓ Configuration file found and loaded")
            
            # Check required sections
            required_sections = ['video', 'shelf_sections', 'detection', 'alerts', 'display']
            for section in required_sections:
                if section in config:
                    print(f"  ✓ Config section '{section}' present")
                else:
                    print(f"  ⚠ Config section '{section}' missing")
            
        except FileNotFoundError:
            print("  ⚠ config.yaml not found - will use defaults")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False

def test_system_modules():
    """Test custom system modules"""
    print("\nTesting custom modules...")
    
    modules = [
        'shelf_detector',
        'empty_detector',
        'yolo_detector',
        'alert_system',
        'config_manager'
    ]
    
    all_good = True
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}.py")
        except ImportError as e:
            print(f"  ✗ {module}.py - {e}")
            all_good = False
    
    return all_good

def run_quick_test():
    """Run a quick end-to-end test"""
    print("\nRunning quick end-to-end test...")
    
    try:
        from main import ShelfMonitoringSystem
        
        # Initialize system
        system = ShelfMonitoringSystem()
        print("  ✓ System initialized")
        
        # Create a test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # Add some shelf-like structures
        cv2.rectangle(test_frame, (50, 100), (590, 150), (139, 69, 19), -1)  # Shelf
        cv2.rectangle(test_frame, (100, 110), (200, 140), (255, 255, 255), -1)  # Product
        cv2.rectangle(test_frame, (250, 110), (350, 140), (255, 255, 255), -1)  # Product
        
        # Process frame
        results = system.process_frame(test_frame)
        print(f"  ✓ Frame processed, detected {len(results)} sections")
        
        # Test visualization
        visual_frame = system.visualize_frame(test_frame, results)
        print("  ✓ Visualization successful")
        
        return True
    except Exception as e:
        print(f"  ✗ End-to-end test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Shelf Monitoring System - Setup Test ===\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("OpenCV Functionality", test_opencv),
        ("Camera Access", test_camera),
        ("YOLO Functionality", test_yolo),
        ("Configuration", test_config),
        ("Custom Modules", test_system_modules),
        ("End-to-End Test", run_quick_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python demo.py' to see the system in action")
        print("2. Run 'python main.py' to start real-time monitoring")
        print("3. Use 'python config_manager.py create-sample' to create config")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check camera permissions and availability")
        print("3. Ensure all .py files are in the same directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
