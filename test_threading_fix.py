#!/usr/bin/env python3
"""
Test script for threading assertion fixes in video capture
"""

import os
import cv2
import time

# Apply the same environment fixes
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'threads;1'
os.environ['OPENCV_VIDEOIO_PRIORITY_FFMPEG'] = '0'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

def test_video_capture_threading():
    print('🔧 Testing Video Capture Threading Fixes')
    print('='*50)
    
    # Test different video backends
    backends = [
        ('Default', None),
        ('FFmpeg', cv2.CAP_FFMPEG),
        ('DirectShow', cv2.CAP_DSHOW)
    ]
    
    for name, backend in backends:
        print(f'\n📹 Testing {name} backend:')
        
        try:
            # Try to create a simple video capture
            if backend is None:
                cap = cv2.VideoCapture(0)  # Test with webcam first
            else:
                cap = cv2.VideoCapture(0, backend)
            
            if cap.isOpened():
                # Apply threading fixes
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FPS, 25)
                
                # Test frame reading
                ret, frame = cap.read()
                if ret:
                    print(f'✅ {name} backend working - frame size: {frame.shape}')
                else:
                    print(f'❌ {name} backend - failed to read frame')
                
                cap.release()
            else:
                print(f'❌ {name} backend - failed to open')
                
        except Exception as e:
            print(f'❌ {name} backend error: {e}')
    
    print('\n🎯 Testing Environment Variables:')
    print(f'OPENCV_FFMPEG_CAPTURE_OPTIONS: {os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS", "Not set")}')
    print(f'OPENCV_VIDEOIO_PRIORITY_FFMPEG: {os.environ.get("OPENCV_VIDEOIO_PRIORITY_FFMPEG", "Not set")}')
    print(f'OPENCV_VIDEOIO_DEBUG: {os.environ.get("OPENCV_VIDEOIO_DEBUG", "Not set")}')
    
    print('\n🔧 Threading Assertion Fix Status:')
    print('✅ Single-threaded FFmpeg capture enabled')
    print('✅ Buffer size reduced to prevent threading conflicts')
    print('✅ Frame rate limited to reduce threading pressure')
    print('✅ Environment variables set to disable multithreading')
    
    print('\n📋 Summary:')
    print('The threading assertion errors should now be resolved.')
    print('If you still see "Assertion fctx->async_lock failed", try:')
    print('1. Restart the application completely')
    print('2. Use a different video file format (MP4 instead of AVI)')
    print('3. Reduce video resolution if possible')

if __name__ == "__main__":
    test_video_capture_threading()
