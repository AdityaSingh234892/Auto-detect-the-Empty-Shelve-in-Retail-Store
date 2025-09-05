"""
Demonstration script showing the enhanced YOLO shelf monitoring system
"""
import cv2
import numpy as np
from improved_yolo_detector import ImprovedYOLODetector
import time

def create_demo_sequence():
    """Create a sequence showing the enhanced detection in action"""
    print("🎬 Creating Enhanced YOLO Detection Demonstration")
    print("=" * 50)
    
    detector = ImprovedYOLODetector(sensitivity=0.7)
    
    # Create demo images with different shelf states
    demo_frames = []
    
    # Frame 1: Empty shelf
    empty_shelf = np.ones((400, 600, 3), dtype=np.uint8) * 250
    cv2.rectangle(empty_shelf, (50, 50), (550, 350), (245, 245, 245), 2)
    cv2.putText(empty_shelf, "EMPTY SHELF DEMONSTRATION", (80, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
    demo_frames.append(("Empty Shelf", empty_shelf))
    
    # Frame 2: Partially stocked
    partial_shelf = np.ones((400, 600, 3), dtype=np.uint8) * 245
    cv2.rectangle(partial_shelf, (50, 50), (550, 350), (240, 240, 240), 2)
    # Add some products on left side
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i, color in enumerate(colors):
        x, y = 70 + i * 60, 80
        cv2.rectangle(partial_shelf, (x, y), (x + 50, y + 120), color, -1)
        cv2.rectangle(partial_shelf, (x, y), (x + 50, y + 120), (0, 0, 0), 2)
        cv2.putText(partial_shelf, f"P{i+1}", (x+15, y+65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(partial_shelf, "PARTIALLY STOCKED SHELF", (100, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
    demo_frames.append(("Partial Shelf", partial_shelf))
    
    # Frame 3: Fully stocked
    stocked_shelf = np.ones((400, 600, 3), dtype=np.uint8) * 180
    cv2.rectangle(stocked_shelf, (50, 50), (550, 350), (170, 170, 170), 2)
    # Add many products
    product_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
                     (255, 0, 255), (0, 255, 255), (128, 255, 0), (255, 128, 0)]
    
    for i in range(8):
        x = 70 + (i % 4) * 110
        y = 80 + (i // 4) * 130
        color = product_colors[i]
        w, h = 80, 100
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), color, -1)
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(stocked_shelf, f"ITEM", (x+10, y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(stocked_shelf, f"{i+1:02d}", (x+20, y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Add texture
        for j in range(3):
            cv2.line(stocked_shelf, (x+10, y+70+j*10), (x+w-10, y+70+j*10), (255, 255, 255), 1)
    
    cv2.putText(stocked_shelf, "FULLY STOCKED SHELF", (120, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
    demo_frames.append(("Stocked Shelf", stocked_shelf))
    
    # Analyze each frame and create annotated versions
    print("\\n🔍 Analyzing Each Shelf State:")
    annotated_frames = []
    
    for name, frame in demo_frames:
        print(f"\\n📊 Analyzing {name}...")
        
        # Extract shelf region (center area)
        shelf_roi = frame[60:340, 60:540]
        
        # Analyze with improved detector
        result = detector.analyze_shelf_region(shelf_roi, name, time.time())
        
        # Create annotated version
        annotated = frame.copy()
        
        # Add detection results
        visual_feedback = result['visual_feedback']
        color = visual_feedback['color']
        thickness = visual_feedback['thickness']
        
        # Draw detection border
        cv2.rectangle(annotated, (60, 60), (540, 340), color, thickness)
        
        # Add detection information overlay
        info_y = 370
        cv2.rectangle(annotated, (50, info_y), (550, 395), (0, 0, 0), -1)
        
        status_text = f"Status: {'EMPTY' if result['is_empty'] else 'STOCKED'} | "
        status_text += f"Confidence: {result['confidence']:.1%} | "
        status_text += f"Alert: {result['alert_level']}"
        
        cv2.putText(annotated, status_text, (60, info_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add method scores
        method_scores = result['method_scores']
        scores_text = "Methods: "
        for method, score in list(method_scores.items())[:3]:  # Show first 3
            scores_text += f"{method.split('_')[0][:3]}:{score:.2f} "
        
        cv2.putText(annotated, scores_text, (60, info_y + 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Print analysis results
        print(f"   Status: {'❌ EMPTY' if result['is_empty'] else '✅ STOCKED'}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Visual State: {result['visual_state']}")
        print(f"   Alert Level: {result['alert_level']}")
        
        method_breakdown = "   Methods: "
        for method, score in method_scores.items():
            method_breakdown += f"{method.split('_')[0][:3]}:{score:.2f} "
        print(method_breakdown)
        
        annotated_frames.append((name, annotated))
        
        # Save individual frame
        filename = f"demo_{name.lower().replace(' ', '_')}.jpg"
        cv2.imwrite(filename, annotated)
        print(f"   💾 Saved: {filename}")
    
    # Create comparison image
    print(f"\\n🖼️ Creating Comparison Image...")
    comparison = np.zeros((450, 1800, 3), dtype=np.uint8)
    
    for i, (name, frame) in enumerate(annotated_frames):
        x_start = i * 600
        comparison[25:425, x_start:x_start+600] = frame
        
        # Add title
        cv2.putText(comparison, f"{i+1}. {name}", (x_start + 10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Add main title
    cv2.rectangle(comparison, (0, 0), (1800, 50), (50, 50, 50), -1)
    cv2.putText(comparison, "Enhanced YOLO Shelf Detection Demonstration", (400, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    cv2.imwrite("enhanced_detection_demo.jpg", comparison)
    print(f"💾 Saved comparison: enhanced_detection_demo.jpg")
    
    return annotated_frames

def create_features_showcase():
    """Create a showcase of the enhanced features"""
    print(f"\\n🌟 Creating Features Showcase")
    print("-" * 30)
    
    # Create feature showcase image
    showcase = np.ones((800, 1200, 3), dtype=np.uint8) * 240
    
    # Title
    cv2.rectangle(showcase, (0, 0), (1200, 80), (50, 50, 150), -1)
    cv2.putText(showcase, "Enhanced YOLO Shelf Detection Features", (200, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)
    
    # Feature boxes
    features = [
        {
            'title': '1. Multi-Stage Analysis',
            'description': ['• Uniformity Analysis', '• Object Detection', '• Color Analysis', 
                          '• Texture Analysis', '• Structure Analysis'],
            'pos': (50, 100)
        },
        {
            'title': '2. Enhanced Visual Feedback',
            'description': ['• Color-coded alerts', '• Pulsing for critical alerts', 
                          '• Confidence percentages', '• Real-time status', '• Method scores'],
            'pos': (650, 100)
        },
        {
            'title': '3. Better Empty Detection',
            'description': ['• Uniformity-based analysis', '• Meaningful object filtering', 
                          '• Multi-indicator classification', '• Improved thresholds', '• Sensitivity control'],
            'pos': (50, 350)
        },
        {
            'title': '4. Rich Alert System',
            'description': ['• Multiple alert levels', '• Visual state indicators', 
                          '• Trend analysis', '• Stability metrics', '• Sound notifications'],
            'pos': (650, 350)
        },
        {
            'title': '5. Advanced UI Features',
            'description': ['• Tabbed alert display', '• Real-time method scores', 
                          '• Detection status overview', '• 4-corner adjustment', '• Enhanced overlays'],
            'pos': (50, 600)
        },
        {
            'title': '6. Performance Improvements',
            'description': ['• Better accuracy', '• Reduced false positives', 
                          '• Faster processing', '• Memory efficient', '• Robust detection'],
            'pos': (650, 600)
        }
    ]
    
    for feature in features:
        x, y = feature['pos']
        w, h = 500, 200
        
        # Feature box
        cv2.rectangle(showcase, (x, y), (x + w, y + h), (255, 255, 255), -1)
        cv2.rectangle(showcase, (x, y), (x + w, y + h), (100, 100, 100), 2)
        
        # Title
        cv2.putText(showcase, feature['title'], (x + 10, y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 150), 2)
        
        # Description
        for i, desc in enumerate(feature['description']):
            cv2.putText(showcase, desc, (x + 20, y + 60 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    cv2.imwrite("enhanced_features_showcase.jpg", showcase)
    print(f"💾 Saved features showcase: enhanced_features_showcase.jpg")

if __name__ == "__main__":
    # Create demonstration
    demo_frames = create_demo_sequence()
    create_features_showcase()
    
    print(f"\\n🎉 Enhanced YOLO Detection Demonstration Complete!")
    print("="*50)
    print("✅ Successfully created:")
    print("  • Individual shelf analysis images")
    print("  • Comparison demonstration image") 
    print("  • Features showcase image")
    print("\\n🚀 The enhanced system provides:")
    print("  • Better empty shelf identification")
    print("  • Rich visual feedback with confidence percentages")
    print("  • Multi-method analysis scoring")
    print("  • Real-time detection status displays")
    print("  • Enhanced alert system with priorities")
    print("\\n✨ Ready for integration with modern_gui_fixed.py!")
