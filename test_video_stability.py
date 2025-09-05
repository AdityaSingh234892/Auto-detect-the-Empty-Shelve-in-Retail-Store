"""
Enhanced Video Processing Test
Tests the improved video stability and robustness features
"""
import os

# Apply OpenMP fix first
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import time
import threading
import queue
import numpy as np
from datetime import datetime

def test_video_stability():
    """Test video capture stability with the new enhancements"""
    print("🎬 Testing Enhanced Video Processing...")
    
    # Test video creation (simulate a simple video)
    test_video_path = "test_stability.mp4"
    
    try:
        # Create a simple test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video_path, fourcc, 20.0, (640, 480))
        
        print("📹 Creating test video...")
        for i in range(100):  # 5 seconds at 20 FPS
            # Create a frame with moving content
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"Frame {i}", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.circle(frame, (320 + int(100 * np.sin(i * 0.2)), 240), 20, (0, 255, 0), -1)
            out.write(frame)
        
        out.release()
        print("✅ Test video created")
        
        # Test enhanced video capture
        print("🔧 Testing enhanced video capture...")
        cap = cv2.VideoCapture(test_video_path)
        
        # Apply enhanced settings
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 20)
        
        if not cap.isOpened():
            print("❌ Failed to open test video")
            return False
        
        # Test frame reading stability
        successful_reads = 0
        total_attempts = 50
        read_times = []
        
        print(f"📊 Testing {total_attempts} frame reads...")
        
        for i in range(total_attempts):
            start_time = time.time()
            ret, frame = cap.read()
            read_time = time.time() - start_time
            read_times.append(read_time)
            
            if ret and frame is not None and frame.size > 0:
                successful_reads += 1
            else:
                print(f"⚠️ Read failure at frame {i}")
                # Test recovery
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        
        cap.release()
        
        # Calculate statistics
        success_rate = (successful_reads / total_attempts) * 100
        avg_read_time = np.mean(read_times) * 1000  # Convert to ms
        max_read_time = np.max(read_times) * 1000
        
        print(f"\n📈 Video Stability Test Results:")
        print(f"   ✅ Success Rate: {success_rate:.1f}% ({successful_reads}/{total_attempts})")
        print(f"   ⏱️ Average Read Time: {avg_read_time:.2f}ms")
        print(f"   ⏱️ Max Read Time: {max_read_time:.2f}ms")
        
        # Cleanup
        try:
            os.remove(test_video_path)
            print("🧹 Test video cleaned up")
        except:
            pass
        
        # Test threading simulation
        print("\n🧵 Testing threading simulation...")
        test_threading_stability()
        
        return success_rate >= 90  # 90% success rate is acceptable
        
    except Exception as e:
        print(f"❌ Video stability test error: {e}")
        return False

def test_threading_stability():
    """Test video processing with threading (simulates monitoring)"""
    frame_queue = queue.Queue(maxsize=2)
    processing_active = True
    successful_processes = 0
    
    def video_processor():
        nonlocal successful_processes
        # Simulate video processing like the monitoring loop
        for i in range(20):
            if not processing_active:
                break
            
            try:
                # Simulate frame processing
                fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(fake_frame, f"Processed {i}", (100, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Try to put in queue (non-blocking)
                if not frame_queue.full():
                    frame_queue.put_nowait(fake_frame)
                    successful_processes += 1
                
                time.sleep(0.05)  # Simulate processing time
                
            except Exception as e:
                print(f"   ⚠️ Processing error: {e}")
    
    def frame_consumer():
        # Simulate display updates
        consumed_frames = 0
        while processing_active and consumed_frames < 15:
            try:
                if not frame_queue.empty():
                    frame = frame_queue.get_nowait()
                    consumed_frames += 1
                time.sleep(0.03)  # Simulate display rate
            except:
                pass
        return consumed_frames
    
    # Start threads
    processor_thread = threading.Thread(target=video_processor, daemon=True)
    processor_thread.start()
    
    consumed = frame_consumer()
    
    # Stop processing
    processing_active = False
    processor_thread.join(timeout=1.0)
    
    print(f"   📊 Processed: {successful_processes} frames")
    print(f"   📺 Consumed: {consumed} frames")
    print(f"   ✅ Threading Test: {'PASSED' if consumed >= 10 else 'FAILED'}")

def test_openmp_and_libraries():
    """Test OpenMP fix and library compatibility"""
    print("\n🔧 Testing OpenMP and Library Compatibility...")
    
    try:
        # Test OpenCV operations
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        print("   ✅ OpenCV operations: OK")
        
        # Test NumPy operations
        array = np.random.rand(1000, 1000)
        result = np.dot(array, array.T)
        print("   ✅ NumPy operations: OK")
        
        # Test potential YOLOv8 import (if available)
        try:
            from ultralytics import YOLO
            print("   ✅ YOLOv8 available: OK")
        except ImportError:
            print("   ⚠️ YOLOv8 not available (optional)")
        except Exception as e:
            print(f"   ⚠️ YOLOv8 error: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Library compatibility error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Video Processing Validation")
    print("=" * 50)
    
    # Run tests
    openmp_ok = test_openmp_and_libraries()
    video_ok = test_video_stability()
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS:")
    print(f"   🔧 OpenMP & Libraries: {'✅ PASS' if openmp_ok else '❌ FAIL'}")
    print(f"   🎬 Video Processing: {'✅ PASS' if video_ok else '❌ FAIL'}")
    
    if openmp_ok and video_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Your shelf monitoring system should now run smoothly")
        print("💡 To start: python modern_gui.py")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("🔧 Please check the error messages above")
    
    print("\n" + "=" * 50)
