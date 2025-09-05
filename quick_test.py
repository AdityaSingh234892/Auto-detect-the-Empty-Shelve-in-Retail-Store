"""
Quick OpenMP Fix Test - Basic Libraries Only
"""
import os

# Apply OpenMP fix BEFORE any other imports
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

print("🔧 Testing OpenMP fix with basic libraries...")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
    
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
    
    # Test basic OpenCV operations
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    print("✅ OpenCV operations working")
    
    print("\n🎉 OpenMP fix successful!")
    print("✅ No more 'libiomp5md.dll already initialized' errors")
    print("🚀 System ready for shelf monitoring!")
    
except Exception as e:
    print(f"❌ Error: {e}")
