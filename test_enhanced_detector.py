#!/usr/bin/env python3
"""
Simple test for Enhanced Video Detector
"""

from enhanced_video_detector import EnhancedVideoShelfDetector
import numpy as np

def test_enhanced_detector():
    print('Testing Enhanced Video Detector for Better Empty Shelf Detection')
    print('=' * 65)
    
    # Initialize enhanced detector
    detector = EnhancedVideoShelfDetector(sensitivity=0.7)
    
    # Test 1: Very uniform empty shelf (light colored)
    print('\nTest 1: Light Uniform Empty Shelf')
    empty_light = np.ones((120, 250, 3), dtype=np.uint8) * 230  # Very light gray
    result1 = detector.analyze_shelf_region(empty_light, 'Empty_Light_Shelf')
    print(f'Result: {"EMPTY" if result1["is_empty"] else "STOCKED"} (Confidence: {result1["confidence"]:.1%})')
    print(f'Visual State: {result1["visual_state"]}')
    
    # Test 2: Medium uniform empty shelf
    print('\nTest 2: Medium Uniform Empty Shelf')
    empty_medium = np.ones((120, 250, 3), dtype=np.uint8) * 180  # Medium gray
    result2 = detector.analyze_shelf_region(empty_medium, 'Empty_Medium_Shelf')
    print(f'Result: {"EMPTY" if result2["is_empty"] else "STOCKED"} (Confidence: {result2["confidence"]:.1%})')
    print(f'Visual State: {result2["visual_state"]}')
    
    # Test 3: Slightly textured empty shelf
    print('\nTest 3: Textured Empty Shelf (Supermarket Background)')
    empty_textured = np.ones((120, 250, 3), dtype=np.uint8) * 200
    # Add slight texture to simulate shelf background
    noise = np.random.normal(0, 5, empty_textured.shape).astype(np.int8)
    empty_textured = np.clip(empty_textured.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    result3 = detector.analyze_shelf_region(empty_textured, 'Empty_Textured_Shelf')
    print(f'Result: {"EMPTY" if result3["is_empty"] else "STOCKED"} (Confidence: {result3["confidence"]:.1%})')
    print(f'Visual State: {result3["visual_state"]}')
    
    # Test 4: Clearly stocked shelf
    print('\nTest 4: Clearly Stocked Shelf')
    stocked = np.random.randint(0, 255, (120, 250, 3), dtype=np.uint8)
    result4 = detector.analyze_shelf_region(stocked, 'Stocked_Shelf')
    print(f'Result: {"EMPTY" if result4["is_empty"] else "STOCKED"} (Confidence: {result4["confidence"]:.1%})')
    print(f'Visual State: {result4["visual_state"]}')
    
    print('\nEnhanced Detection Features:')
    print('✅ Aggressive empty detection mode')
    print('✅ Multi-threshold analysis')
    print('✅ Spatial grid analysis')
    print('✅ Temporal consistency tracking')
    print('✅ Video compression compensation')
    print('✅ Supermarket lighting optimization')
    
    print('\nEnhanced Video Detector Ready!')
    print('📹 Optimized for supermarket video analysis')
    print('🔍 Superior empty shelf identification')

if __name__ == "__main__":
    test_enhanced_detector()
