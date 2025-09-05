# 🚀 Smart Shelf Monitor Pro - User Guide

## 🎯 Overview

The **Smart Shelf Monitor Pro** is a modern, interactive shelf monitoring system that allows you to:

1. **📹 Load Video Sources** - Camera or video files
2. **🎯 Interactively Select Shelves** - Click and drag to define monitoring areas
3. **🔍 Advanced Detection** - Multi-method empty shelf detection
4. **🚨 Real-time Alerts** - Visual and audio notifications with detailed information
5. **📊 Live Statistics** - Real-time monitoring statistics
6. **⚙️ Customizable Settings** - Adjust sensitivity and preferences

---

## 🎮 Step-by-Step Usage

### **Step 1: Launch the Application**
```bash
# Method 1: Use the launcher (Windows)
launch_modern.bat

# Method 2: Direct Python execution
python modern_gui.py
```

### **Step 2: Load Video Source**
1. **Select Source Type:**
   - Choose "Camera" for live webcam feed
   - Choose "Video File" for recorded video

2. **For Video File:**
   - Click "Browse" to select your video file
   - Supported formats: MP4, AVI, MOV, MKV, WMV

3. **Click "📹 Load Video"**
   - The video will start playing in the main display area
   - Status will change to "● Video Loaded"

### **Step 3: Define Shelf Areas**
1. **Click "🎯 Select Shelves"**
   - Button changes to "✋ Stop Selection"
   - Instruction text guides you through the process

2. **Draw Shelf Regions:**
   - **Click and drag** on the video to draw rectangles around shelf areas
   - Each rectangle represents a shelf section to monitor
   - Make sure to cover the entire shelf area you want to monitor

3. **Name Your Shelves:**
   - After drawing each rectangle, a dialog appears
   - Enter a descriptive name (e.g., "Bread Section", "Milk Shelf", "Snacks")
   - Click "OK" to save the shelf region

4. **Repeat for All Shelves:**
   - Continue drawing rectangles for all shelf areas
   - You can define multiple shelves of different sizes

5. **Finish Selection:**
   - Click "✋ Stop Selection" when done
   - All defined shelves appear in the "🏪 Defined Shelves" list

### **Step 4: Configure Settings**
1. **Detection Sensitivity:** (0.3 - 0.9)
   - **Low (0.3):** Less sensitive - only detects very empty shelves
   - **Medium (0.7):** Balanced detection
   - **High (0.9):** More sensitive - detects partially empty shelves

2. **Enable Alert Sounds:** Check to hear audio alerts

3. **Auto-save Alert Log:** Automatically save alerts to file

### **Step 5: Start Monitoring**
1. **Click "▶️ Start Monitoring"**
   - Button changes to "⏹️ Stop Monitoring"
   - Status changes to "● Monitoring Active"
   - Real-time analysis begins

2. **Monitor the Display:**
   - **Green rectangles:** Shelves with products (OK)
   - **Red rectangles:** Empty shelves (ALERT)
   - **Confidence percentages** shown for each detection

### **Step 6: View Results**
1. **Live Video Feed:**
   - Real-time overlay showing shelf status
   - System information panel (top-right)
   - Frame count, FPS, and timestamp

2. **Active Alerts Panel:**
   - Detailed alert messages
   - Timestamps and confidence scores
   - Detection method breakdown

3. **Statistics Panel:**
   - Number of monitored shelves
   - Currently empty shelves
   - Total alerts generated
   - Processing FPS

---

## 🎨 Interface Features

### **Modern Dark Theme**
- Professional dark color scheme
- High contrast for better visibility
- Color-coded status indicators

### **Real-time Overlays**
- **Green:** Shelf OK (products detected)
- **Red:** Shelf Empty (alert condition)
- **System info:** Frame count, FPS, timestamp
- **Confidence scores:** Detection accuracy

### **Alert System**
- **Visual:** On-screen rectangles and text
- **Audio:** System beeps and sounds
- **Logging:** Automatic alert history
- **Detailed info:** Method-specific scores

### **Interactive Controls**
- **Drag-and-drop:** Shelf selection
- **Real-time settings:** Adjust sensitivity during monitoring
- **Shelf management:** Add, delete, clear shelves
- **Status indicators:** Color-coded system status

---

## 📊 Understanding Detection Results

### **Alert Message Format**
```
🚨 SHELF EMPTY ALERT 🚨
Shelf: Bread Section
Time: 14:30:45
Confidence: 87%
Stability: 8/10
Detection Methods:
  Variance: 92%
  Edge: 85%
  Color: 80%
  Texture: 90%
  Contour: 88%
```

### **Confidence Levels**
- **90-100%:** Very confident - definitely empty
- **70-89%:** High confidence - likely empty
- **50-69%:** Medium confidence - possibly empty
- **Below 50%:** Low confidence - probably not empty

### **Stability Score**
- **8-10/10:** Very stable detection over time
- **5-7/10:** Moderately stable
- **Below 5/10:** Unstable - may be false detection

---

## ⚙️ Advanced Features

### **Multiple Detection Methods**
1. **Pixel Variance:** Detects uniform empty areas
2. **Edge Density:** Measures texture and detail levels
3. **Color Distribution:** Analyzes color patterns
4. **Texture Analysis:** Examines surface patterns
5. **Contour Analysis:** Detects shape patterns

### **Temporal Stability**
- **History tracking:** Analyzes recent frames
- **Weighted decisions:** Recent frames have more influence
- **False positive reduction:** Filters out noise
- **Alert cooldown:** Prevents alert spam

### **Adaptive Sensitivity**
- **Real-time adjustment:** Change during monitoring
- **Per-method tuning:** Advanced sensitivity control
- **Environmental adaptation:** Adjusts to lighting conditions

---

## 🛠️ Troubleshooting

### **Common Issues**

1. **Camera Not Detected**
   - Check camera permissions
   - Try different camera indices (0, 1, 2)
   - Ensure camera is not used by other applications

2. **Video File Won't Load**
   - Check file format (MP4, AVI, MOV, MKV, WMV)
   - Verify file path and permissions
   - Try converting to MP4 format

3. **Poor Detection Accuracy**
   - Adjust sensitivity settings (try 0.6-0.8)
   - Ensure good lighting conditions
   - Define shelf areas more precisely
   - Check that shelf areas don't overlap

4. **Performance Issues**
   - Close other applications
   - Use lower resolution video
   - Reduce number of monitored shelves
   - Check system resources

### **Tips for Better Results**

1. **Shelf Selection:**
   - Draw tight rectangles around actual shelf areas
   - Avoid including background or non-shelf areas
   - Make sure shelves are well-lit
   - Avoid overlapping regions

2. **Optimal Conditions:**
   - Good, consistent lighting
   - Stable camera position
   - Clear view of shelves
   - Minimal shadows

3. **Sensitivity Tuning:**
   - Start with 0.7 (default)
   - Increase for more sensitive detection
   - Decrease if getting false positives
   - Monitor for a few minutes before adjusting

---

## 📁 Output Files

### **Alert Logs**
- **Filename:** `shelf_alerts_YYYYMMDD.log`
- **Location:** Same folder as application
- **Format:** Timestamped alert records
- **Encoding:** UTF-8 text file

### **Saved Frames**
- **Manual save:** Press 'S' during monitoring
- **Automatic:** When alerts are triggered
- **Format:** JPEG images
- **Naming:** `frame_YYYYMMDD_HHMMSS.jpg`

---

## 🎯 Best Practices

### **For Grocery Stores**
1. Define sections by product type (Bread, Milk, Cereals)
2. Use medium sensitivity (0.6-0.7)
3. Monitor during peak hours
4. Review alert logs daily

### **For Warehouses**
1. Define larger zones by storage area
2. Use higher sensitivity (0.7-0.8)
3. Focus on high-turnover areas
4. Set up automated reporting

### **For Convenience Stores**
1. Monitor key product categories
2. Use lower sensitivity (0.5-0.6) for frequent restocking
3. Enable audio alerts for immediate attention
4. Position camera for best shelf visibility

---

## 🔄 Updates and Maintenance

### **Regular Tasks**
- Review and archive alert logs
- Clean up saved frame images
- Update shelf definitions as needed
- Calibrate sensitivity based on performance

### **System Updates**
- Keep Python and packages updated
- Update YOLO models when available
- Backup configuration settings
- Test with new video sources

---

## 💡 Pro Tips

1. **🎯 Precise Selection:** Take time to carefully define shelf areas
2. **⚡ Performance:** Monitor system resources during operation
3. **📊 Analytics:** Review alert patterns to optimize store layout
4. **🔧 Tuning:** Adjust sensitivity based on actual performance
5. **📱 Integration:** Consider integrating with inventory management systems

---

**Happy Monitoring! 🛒📊**
