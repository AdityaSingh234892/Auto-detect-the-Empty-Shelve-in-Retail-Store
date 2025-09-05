"""
Test the improved YOLO detector with better empty shelf detection
"""
import cv2
import numpy as np
import time
from improved_yolo_detector import ImprovedYOLODetector

def create_realistic_test_images():
    """Create more realistic test images"""
    
    # 1. Truly empty shelf - very uniform, minimal variation
    empty_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 250
    # Add very subtle shelf edges
    cv2.line(empty_shelf, (0, 190), (300, 190), (245, 245, 245), 1)
    cv2.line(empty_shelf, (0, 10), (300, 10), (245, 245, 245), 1)
    # Minimal noise
    noise = np.random.normal(0, 1, empty_shelf.shape).astype(np.int8)
    empty_shelf = np.clip(empty_shelf.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 2. Fully stocked shelf with many distinct products
    stocked_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 160
    
    # Add 12 distinct products with varied colors and textures
    products = [
        {'color': (255, 0, 0), 'pos': (20, 30), 'size': (35, 70)},
        {'color': (0, 255, 0), 'pos': (60, 25), 'size': (40, 75)},
        {'color': (0, 0, 255), 'pos': (105, 35), 'size': (38, 65)},
        {'color': (255, 255, 0), 'pos': (148, 20), 'size': (42, 80)},
        {'color': (255, 0, 255), 'pos': (195, 30), 'size': (36, 70)},
        {'color': (0, 255, 255), 'pos': (235, 25), 'size': (45, 75)},
        
        {'color': (128, 255, 0), 'pos': (25, 110), 'size': (40, 70)},
        {'color': (255, 128, 0), 'pos': (70, 105), 'size': (35, 75)},
        {'color': (128, 0, 255), 'pos': (110, 115), 'size': (42, 65)},
        {'color': (255, 128, 128), 'pos': (155, 100), 'size': (38, 80)},
        {'color': (128, 255, 128), 'pos': (198, 110), 'size': (40, 70)},
        {'color': (128, 128, 255), 'pos': (242, 105), 'size': (37, 75)},
    ]
    
    for product in products:
        x, y = product['pos']
        w, h = product['size']
        color = product['color']
        
        # Draw main product
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), color, -1)
        cv2.rectangle(stocked_shelf, (x, y), (x + w, y + h), (0, 0, 0), 2)
        
        # Add text and texture
        cv2.putText(stocked_shelf, "PROD", (x+3, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        cv2.putText(stocked_shelf, "123", (x+3, y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Add texture lines
        for i in range(3):
            cv2.line(stocked_shelf, (x+5, y+40+i*8), (x+w-5, y+40+i*8), (255, 255, 255), 1)
        
        # Add some highlights and shadows
        cv2.line(stocked_shelf, (x+1, y+1), (x+w-1, y+1), (255, 255, 255), 1)
        cv2.line(stocked_shelf, (x+1, y+h-1), (x+w-1, y+h-1), (100, 100, 100), 1)
    
    # 3. Partially stocked shelf - clear division between stocked and empty
    partial_shelf = np.ones((200, 300, 3), dtype=np.uint8) * 248
    
    # Left side: 3 products
    for i, product in enumerate(products[:3]):
        x, y = product['pos']
        w, h = product['size']
        color = product['color']
        cv2.rectangle(partial_shelf, (x, y), (x + w, y + h), color, -1)
        cv2.rectangle(partial_shelf, (x, y), (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(partial_shelf, f"P{i+1}", (x+8, y+35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Right side: clearly empty
    cv2.rectangle(partial_shelf, (150, 10), (290, 190), (250, 250, 250), 1)
    # Make right side very uniform
    partial_shelf[10:190, 150:290] = 250
    
    # 4. Almost empty - just dust and shelf structure
    almost_empty = np.ones((200, 300, 3), dtype=np.uint8) * 252
    # Add shelf structure
    cv2.line(almost_empty, (0, 190), (300, 190), (248, 248, 248), 1)
    cv2.line(almost_empty, (150, 10), (150, 190), (248, 248, 248), 1)
    # Add some dust/debris
    for i in range(5):
        x, y = np.random.randint(50, 250), np.random.randint(50, 180)
        cv2.circle(almost_empty, (x, y), 2, (240, 240, 240), -1)
    
    return {
        'empty': empty_shelf,
        'stocked': stocked_shelf,
        'partial': partial_shelf,
        'almost_empty': almost_empty
    }

def test_improved_detector():
    """Test the improved detector"""
    print("🚀 Testing Improved YOLO Detector with Better Empty Detection")
    print("=" * 65)
    
    detector = ImprovedYOLODetector(sensitivity=0.7)
    test_images = create_realistic_test_images()
    
    for image_name, image in test_images.items():
        print(f"\n📊 Testing {image_name.upper()} shelf:")
        print("-" * 40)
        
        result = detector.analyze_shelf_region(image, f"Test_{image_name}", time.time())
        
        # Display results
        print(f"🔍 Detection Results:")
        print(f"   Empty Status: {'❌ EMPTY' if result['is_empty'] else '✅ STOCKED'}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Fullness Score: {result['fullness_score']:.1%}")
        print(f"   Visual State: {result['visual_state']}")
        print(f"   Alert Level: {result['alert_level']}")
        print(f"   Should Alert: {'🚨 YES' if result['should_alert'] else '🔕 NO'}")
        
        print(f"\n🎯 Method Breakdown:")
        method_scores = result['method_scores']
        for method, score in method_scores.items():
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {method.replace('_', ' ').title():20}: {bar} {score:.2f}")
        
        # Show detailed analysis
        details = result['details']
        if 'uniformity' in details:
            uniformity = details['uniformity']
            print(f"\n📈 Detailed Analysis:")
            print(f"   Uniformity Score: {uniformity['uniformity_score']:.2f}")
            print(f"   Is Uniform: {'✅ YES' if uniformity['is_uniform'] else '❌ NO'}")
            print(f"   Total Variance: {uniformity['total_variance']:.1f}")
            
        if 'objects' in details:
            objects = details['objects']
            print(f"   Meaningful Objects: {objects['meaningful_object_count']}")
            print(f"   Coverage Ratio: {objects['coverage_ratio']:.2%}")
            
        if 'color' in details:
            color = details['color']
            print(f"   Color Variance: {color['total_color_variance']:.1f}")
            print(f"   Has Diverse Colors: {'✅ YES' if color['has_diverse_colors'] else '❌ NO'}")
        
        # Empty indicators summary
        if 'empty_indicators' in result['details'].get('confidence_calc', {}):
            indicators = result['details']['confidence_calc']['empty_indicators']
            print(f"   Empty Indicators: {indicators}/5")
        
        # Save result image
        display_image = image.copy()
        visual_feedback = result['visual_feedback']
        color = visual_feedback['color']
        thickness = visual_feedback['thickness']
        
        cv2.rectangle(display_image, (5, 5), (image.shape[1]-5, image.shape[0]-5), color, thickness)
        cv2.putText(display_image, f"{result['visual_state']}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(display_image, f"Empty: {'YES' if result['is_empty'] else 'NO'}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(display_image, f"Conf: {result['confidence']:.1%}", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        filename = f"improved_{image_name}_result.jpg"
        cv2.imwrite(filename, display_image)
        print(f"💾 Saved: {filename}")

if __name__ == "__main__":
    test_improved_detector()
    print(f"\n✅ Improved Detection Test Complete!")
    print("Key improvements:")
    print("• Uniformity analysis for better empty detection")
    print("• Meaningful object detection with contrast checks")
    print("• Multi-indicator empty classification")
    print("• Better sensitivity handling")
