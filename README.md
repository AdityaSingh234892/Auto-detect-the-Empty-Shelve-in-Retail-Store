# Shelf Monitoring System

An OpenCV-based Python system for real-time store shelf monitoring and empty section detection using computer vision and YOLO models.

## Features

- **Real-time Video Processing**: Process live camera feeds or recorded videos
- **Shelf Section Detection**: Automatic detection of shelf regions using edge detection and contour analysis
- **Empty Section Identification**: Multi-method approach combining traditional CV techniques with YOLO object detection
- **Smart Alerts**: Real-time on-screen alerts with configurable thresholds and cooldown periods
- **YOLO Integration**: Enhanced product detection using pre-trained YOLO models
- **Modular Design**: Easy adaptation for different store layouts and product types
- **Configuration Management**: YAML-based configuration with interactive setup tools
- **Alert Logging**: Comprehensive logging and export functionality
- **Visual Feedback**: Real-time visualization of detected sections and status

## Installation

1. **Clone or download the project files**

2. **Install required packages**:
```bash
pip install opencv-python numpy ultralytics pillow matplotlib pyyaml playsound
```

3. **For conda users**:
```bash
conda install -c conda-forge opencv numpy pillow matplotlib pyyaml
pip install ultralytics playsound
```

## Quick Start

1. **Create a configuration file**:
```bash
python config_manager.py create-sample
```

2. **Run with webcam**:
```bash
python main.py
```

3. **Process a video file**:
```bash
python main.py --video path/to/your/video.mp4 --output processed_video.mp4
```

## Configuration

### Basic Configuration (config.yaml)

```yaml
video:
  source: 0  # 0 for webcam, or path to video file
  width: 1280
  height: 720
  fps: 30

shelf_sections:
  bread:
    region: [100, 150, 200, 100]  # [x, y, width, height]
    threshold: 0.3  # Empty detection threshold (0-1)
    color: [0, 255, 0]  # RGB color for visualization
  
  milk:
    region: [350, 150, 200, 100]
    threshold: 0.3
    color: [255, 0, 0]

detection:
  canny_low: 50
  canny_high: 150
  empty_threshold: 0.7
  yolo_model: "yolov8n.pt"
  confidence_threshold: 0.5

alerts:
  display_duration: 3000  # milliseconds
  sound_enabled: true
  log_enabled: true
```

### Interactive Configuration Setup

Use a sample frame to interactively define shelf regions:

```bash
python config_manager.py path/to/sample_frame.jpg
```

## System Components

### 1. Shelf Detector (`shelf_detector.py`)
- **Contour-based detection**: Uses Canny edge detection and contour analysis
- **Line-based detection**: Hough transform for detecting shelf edges
- **Configured sections**: Manual region definition support

### 2. Empty Detector (`empty_detector.py`)
- **Pixel variance analysis**: Detects uniform empty areas
- **Color distribution**: Analyzes histogram concentration
- **Edge density**: Measures texture and detail levels
- **Texture analysis**: Gradient-based texture assessment

### 3. YOLO Detector (`yolo_detector.py`)
- **Object detection**: Uses YOLOv8 for product identification
- **Shelf-specific filtering**: Focuses on relevant product categories
- **Product counting**: Counts detected items per section

### 4. Alert System (`alert_system.py`)
- **Real-time alerts**: On-screen notifications with customizable appearance
- **Sound notifications**: Optional audio alerts
- **Logging**: Comprehensive alert history with export functionality
- **Cooldown system**: Prevents alert spam

## Usage Examples

### Real-time Monitoring
```python
from main import ShelfMonitoringSystem

# Initialize system
monitor = ShelfMonitoringSystem("config.yaml")

# Run real-time monitoring
monitor.run_realtime()
```

### Video Processing
```python
# Process a video file
monitor.process_video_file("store_video.mp4", "processed_output.mp4")
```

### Custom Configuration
```python
from config_manager import ConfigManager

config = ConfigManager()
config.add_shelf_section("beverages", [400, 200, 150, 80], threshold=0.4)
config.save_config()
```

## Detection Methods

### Traditional Computer Vision
1. **Edge Detection**: Canny edge detection for shelf boundary identification
2. **Contour Analysis**: Shape-based shelf region detection
3. **Pixel Analysis**: Variance and histogram analysis for emptiness detection
4. **Texture Analysis**: Gradient-based texture measurement

### YOLO Integration
1. **Product Detection**: Identifies specific product types
2. **Count-based Assessment**: Determines emptiness based on product count
3. **Confidence Scoring**: Provides detection confidence levels

### Combined Approach
- Weighted combination of traditional CV and YOLO results
- Adaptive thresholding based on section type
- Cross-validation between methods

## Alert System

### Visual Alerts
- **On-screen notifications**: Real-time overlay on video feed
- **Section highlighting**: Color-coded section status
- **Status indicators**: Green (stocked) / Red (empty)

### Audio Alerts
- **Sound notifications**: Configurable alert sounds
- **System beep fallback**: Built-in alert sound

### Logging
- **File logging**: Timestamped alert records
- **Export functionality**: Alert history export
- **Statistics**: Alert frequency and patterns

## Keyboard Controls

- **'q'**: Quit the application
- **'r'**: Reset all active alerts
- **'s'**: Save current frame as image

## File Structure

```
shelf-monitoring/
├── main.py                 # Main application
├── shelf_detector.py       # Shelf detection algorithms
├── empty_detector.py       # Empty section analysis
├── yolo_detector.py        # YOLO-based detection
├── alert_system.py         # Alert management
├── config_manager.py       # Configuration utilities
├── config.yaml            # Configuration file
└── README.md              # This file
```

## Customization

### Adding New Shelf Sections
1. **Manual configuration**: Edit `config.yaml` directly
2. **Interactive setup**: Use `config_manager.py` with sample frame
3. **Programmatic**: Use ConfigManager class

### Adjusting Detection Parameters
- **Sensitivity**: Modify `empty_threshold` values
- **Edge detection**: Tune `canny_low` and `canny_high`
- **YOLO confidence**: Adjust `confidence_threshold`

### Custom Product Types
- Modify `get_section_product_mapping()` in `yolo_detector.py`
- Add product-specific detection logic
- Configure section-specific thresholds

## Troubleshooting

### Common Issues

1. **Camera not detected**:
   - Check camera permissions
   - Try different source indices (0, 1, 2...)
   - Verify camera is not used by other applications

2. **YOLO model download**:
   - Ensure internet connection for initial model download
   - Models are cached locally after first download

3. **Performance issues**:
   - Reduce video resolution in config
   - Lower FPS settings
   - Disable YOLO detection if not needed

4. **Alert sensitivity**:
   - Adjust `empty_threshold` values
   - Modify individual section thresholds
   - Fine-tune detection parameters

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Features

### Email/SMS Notifications
Extend the `AlertSystem` class to add external notification support:

```python
def send_email_alert(self, section_name, confidence):
    # Add email notification logic
    pass
```

### Database Integration
Add database logging for long-term analysis:

```python
def log_to_database(self, alert_data):
    # Add database logging logic
    pass
```

### API Integration
Create REST API endpoints for remote monitoring:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/status')
def get_status():
    return jsonify(monitor.get_status())
```

## Performance Optimization

- **Frame skipping**: Process every nth frame for better performance
- **ROI processing**: Only process relevant regions
- **Threaded processing**: Separate detection and display threads
- **GPU acceleration**: Use CUDA for YOLO inference

## License

This project is provided as-is for educational and commercial use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review configuration examples
3. Enable debug logging for detailed information
