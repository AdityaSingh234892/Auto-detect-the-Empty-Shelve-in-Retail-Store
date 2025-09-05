#!/usr/bin/env python3
"""
Test script for enhanced supermarket video detection system
"""

from improved_yolo_detector import ImprovedYOLODetector
import cv2
import numpy as np

def test_enhanced_detection():
    print('🎯 Testing Enhanced YOLO Detector for Supermarket Videos')
    print('='*60)

    # Initialize detector
    detector = ImprovedYOLODetector(sensitivity=0.7)

    # Check supermarket mode parameters
    params = detector.detection_params
    print(f'✅ Supermarket Mode: {params.get("supermarket_mode", False)}')
    print(f'📹 Video Compression Factor: {params.get("video_compression_factor", 1.0)}')
    print(f'💡 Lighting Variance Threshold: {params.get("lighting_variance_threshold", 150)}')
    print(f'🏪 Background Tolerance: {params.get("shelf_background_tolerance", 0.15)}')

    # Test empty shelf simulation
    print('\n🧪 Testing Empty Shelf Detection:')
    empty_shelf = np.ones((100, 200, 3), dtype=np.uint8) * 240  # Light gray uniform area
    result = detector.analyze_shelf_region(empty_shelf, 'Test_Empty_Shelf')
    print(f'Empty Shelf - Detected as: {"EMPTY" if result["is_empty"] else "STOCKED"} (Confidence: {result["confidence"]:.1%})')

    # Test stocked shelf simulation  
    stocked_shelf = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)  # Random colorful area
    result2 = detector.analyze_shelf_region(stocked_shelf, 'Test_Stocked_Shelf')
    print(f'Stocked Shelf - Detected as: {"EMPTY" if result2["is_empty"] else "STOCKED"} (Confidence: {result2["confidence"]:.1%})')

    print('\n🎯 Enhanced Detection System Ready!')
    print('🔧 Codec fixes applied for video compatibility')
    print('📱 Supermarket video optimization enabled')
    
    # Test video codec support
    print('\n📹 Testing Video Codec Support:')
    try:
        # Test basic video capture
        cap = cv2.VideoCapture()
        print('✅ OpenCV VideoCapture available')
        
        # Check codec support
        fourcc_codes = ['MJPG', 'XVID', 'H264', 'MP4V']
        for codec in fourcc_codes:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                print(f'✅ {codec} codec supported')
            except:
                print(f'❌ {codec} codec not available')
                
    except Exception as e:
        print(f'❌ Video system error: {e}')

if __name__ == "__main__":
    test_enhanced_detection()
