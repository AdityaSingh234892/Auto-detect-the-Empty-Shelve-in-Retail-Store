"""
Modern Interactive Shelf Monitoring System
Features shelf selection, real-time monitoring, and attractive UI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import threading
import time
from PIL import Image, ImageTk
import queue
import os
import numpy as np
import json
from datetime import datetime

class ModernShelfMonitoringApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Shelf Monitor Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_card': '#3d3d3d',
            'accent': '#0078d4',
            'success': '#107c10',
            'warning': '#ffb900',
            'error': '#d13438',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # System state
        self.video_source = None
        self.cap = None
        self.current_frame = None
        self.shelf_regions = []  # Format: [(corner_points, name), ...]
        self.is_monitoring = False
        self.is_selecting = False
        self.is_adjusting_points = False
        self.adjusting_shelf_index = -1
        self.adjusting_corner = -1
        self.selection_start = None
        self.temp_selection = None
        self.video_loaded = False
        
        # Queues for thread communication
        self.frame_queue = queue.Queue(maxsize=3)
        self.alert_queue = queue.Queue()
        
        # On-screen message system
        self.on_screen_messages = []
        self.message_id_counter = 0
        
        # Statistics
        self.total_alerts = 0
        self.empty_shelves_count = 0
        self.fps_count = 0
        
        self.setup_styles()
        self.create_main_interface()
        
        # Start update loops
        self.root.after(50, self.update_display)
        self.root.after(1000, self.update_alerts)
        self.root.after(100, self.update_on_screen_messages)
    
    def setup_styles(self):
        """Setup modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background=self.colors['bg_secondary'])
        style.configure('Card.TFrame', background=self.colors['bg_card'], relief='raised', borderwidth=1)
        style.configure('Modern.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'])
        style.configure('Title.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'], font=('Segoe UI', 16, 'bold'))
    
    def create_main_interface(self):
        """Create the main interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Video and selection
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_secondary'], relief='raised', bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_video_panel(left_panel)
        
        # Right panel - Controls and information
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_secondary'], relief='raised', bd=2, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_control_panel(right_panel)
    
    def create_header(self, parent):
        """Create modern header"""
        header = tk.Frame(parent, bg=self.colors['bg_secondary'], height=80, relief='raised', bd=2)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)
        
        # Title and status
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="🛒 Smart Shelf Monitor Pro", 
                              font=('Segoe UI', 20, 'bold'), 
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_frame = tk.Frame(title_frame, bg=self.colors['bg_secondary'])
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(self.status_frame, text="● Ready", 
                                    font=('Segoe UI', 12, 'bold'), 
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['success'])
        self.status_label.pack()
        
        self.time_label = tk.Label(self.status_frame, text="", 
                                  font=('Segoe UI', 10), 
                                  bg=self.colors['bg_secondary'], 
                                  fg=self.colors['text_secondary'])
        self.time_label.pack()
        
        # Update time
        self.update_time()
    
    def create_video_panel(self, parent):
        """Create video display panel"""
        video_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video controls
        controls_frame = tk.Frame(video_frame, bg=self.colors['bg_card'], height=60, relief='raised', bd=1)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Source selection
        source_frame = tk.Frame(controls_frame, bg=self.colors['bg_card'])
        source_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(source_frame, text="Video Source:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.source_var = tk.StringVar(value="Video File")
        source_combo = ttk.Combobox(source_frame, textvariable=self.source_var, 
                                   values=["Camera", "Video File"], state="readonly", width=12)
        source_combo.pack(side=tk.LEFT, padx=(0, 10))
        source_combo.bind('<<ComboboxSelected>>', self.on_source_change)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(source_frame, textvariable=self.file_path_var, width=30,
                                  bg=self.colors['bg_secondary'], fg=self.colors['text_primary'], 
                                  insertbackground=self.colors['text_primary'])
        self.file_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(source_frame, text="Browse", command=self.browse_file,
                              bg=self.colors['accent'], fg='white', font=('Segoe UI', 9, 'bold'),
                              relief='flat', padx=10)
        browse_btn.pack(side=tk.LEFT)
        
        # Main action buttons
        action_frame = tk.Frame(controls_frame, bg=self.colors['bg_card'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        self.load_video_btn = tk.Button(action_frame, text="📹 Load Video", command=self.load_video,
                                       bg=self.colors['accent'], fg='white', font=('Segoe UI', 10, 'bold'),
                                       relief='flat', padx=15, pady=5)
        self.load_video_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_shelf_btn = tk.Button(action_frame, text="🎯 Select Areas", command=self.toggle_selection,
                                         bg=self.colors['warning'], fg='black', font=('Segoe UI', 10, 'bold'),
                                         relief='flat', padx=15, pady=5, state=tk.DISABLED)
        self.select_shelf_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.monitor_btn = tk.Button(action_frame, text="▶️ Start Monitoring", command=self.toggle_monitoring,
                                    bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=5, state=tk.DISABLED)
        self.monitor_btn.pack(side=tk.LEFT)
        
        # Video display
        video_display_frame = tk.Frame(video_frame, bg=self.colors['bg_card'], relief='raised', bd=2)
        video_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.video_canvas = tk.Canvas(video_display_frame, bg='black', highlightthickness=0)
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind mouse events for shelf selection
        self.video_canvas.bind("<Button-1>", self.on_canvas_click)
        self.video_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.video_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Instructions label
        self.instruction_frame = tk.Frame(video_display_frame, bg='black')
        self.instruction_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER, width=400, height=60)
        
        self.instruction_label = tk.Label(self.instruction_frame, 
                                         text="Load a video source to start", 
                                         font=('Segoe UI', 11, 'bold'),
                                         bg='#2d2d2d', fg='white',
                                         pady=10, padx=20,
                                         relief='raised', bd=2)
        self.instruction_label.pack(fill=tk.BOTH, expand=True)
    
    def create_control_panel(self, parent):
        """Create control and information panel"""
        control_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Shelf regions section
        shelf_section = self.create_card(control_frame, "🏪 Defined Areas", 200)
        
        self.shelf_listbox = tk.Listbox(shelf_section, bg=self.colors['bg_secondary'], 
                                       fg=self.colors['text_primary'], 
                                       selectbackground=self.colors['accent'],
                                       font=('Segoe UI', 10), height=8)
        self.shelf_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        shelf_buttons = tk.Frame(shelf_section, bg=self.colors['bg_card'])
        shelf_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(shelf_buttons, text="🗑️ Delete", command=self.delete_shelf,
                 bg=self.colors['error'], fg='white', font=('Segoe UI', 9, 'bold'),
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(shelf_buttons, text="🔄 Clear All", command=self.clear_shelves,
                 bg=self.colors['warning'], fg='black', font=('Segoe UI', 9, 'bold'),
                 relief='flat', padx=10).pack(side=tk.RIGHT)
        
        # Statistics section
        stats_section = self.create_card(control_frame, "📊 Statistics", 150)
        
        self.stats_frame = tk.Frame(stats_section, bg=self.colors['bg_card'])
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create stat items
        self.create_stat_item(self.stats_frame, "Areas", "0", "🏪")
        self.create_stat_item(self.stats_frame, "Empty", "0", "📦")
        self.create_stat_item(self.stats_frame, "Alerts", "0", "🚨")
        self.create_stat_item(self.stats_frame, "FPS", "0", "⚡")
        
        # Settings section
        settings_section = self.create_card(control_frame, "⚙️ Settings", 120)
        
        settings_grid = tk.Frame(settings_section, bg=self.colors['bg_card'])
        settings_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Sensitivity setting
        tk.Label(settings_grid, text="Sensitivity:", bg=self.colors['bg_card'], 
                fg=self.colors['text_primary'], font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.sensitivity_var = tk.DoubleVar(value=0.7)
        sensitivity_scale = tk.Scale(settings_grid, from_=0.3, to=0.9, resolution=0.1,
                                   orient=tk.HORIZONTAL, variable=self.sensitivity_var,
                                   bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                                   highlightthickness=0, length=200)
        sensitivity_scale.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # Alert sound setting
        self.sound_var = tk.BooleanVar(value=True)
        sound_check = tk.Checkbutton(settings_grid, text="Alert Sounds", 
                                   variable=self.sound_var, bg=self.colors['bg_card'],
                                   fg=self.colors['text_primary'], font=('Segoe UI', 9),
                                   selectcolor=self.colors['bg_secondary'])
        sound_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Alerts display with enhanced visual feedback
        alert_section = self.create_card(control_frame, "🚨 Live Alerts & Detection Status", 250)
        
        # Create tabbed alert display
        alert_notebook = ttk.Notebook(alert_section)
        alert_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Alert log tab
        alert_log_frame = tk.Frame(alert_notebook, bg=self.colors['bg_card'])
        alert_notebook.add(alert_log_frame, text="📝 Alert Log")
        
        self.alert_text = tk.Text(alert_log_frame, bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text_primary'], font=('Segoe UI', 9),
                                 wrap=tk.WORD, height=6)
        self.alert_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Detection status tab
        status_frame = tk.Frame(alert_notebook, bg=self.colors['bg_card'])
        alert_notebook.add(status_frame, text="📊 Detection Status")
        
        # Real-time detection display
        self.detection_display = tk.Frame(status_frame, bg=self.colors['bg_card'])
        self.detection_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Method scores tab
        scores_frame = tk.Frame(alert_notebook, bg=self.colors['bg_card'])
        alert_notebook.add(scores_frame, text="🎯 Method Scores")
        
        self.scores_display = tk.Frame(scores_frame, bg=self.colors['bg_card'])
        self.scores_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def create_card(self, parent, title, height):
        """Create a modern card widget"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', bd=1, height=height)
        card.pack(fill=tk.X, pady=(0, 10))
        card.pack_propagate(False)
        
        header = tk.Frame(card, bg=self.colors['accent'], height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 11, 'bold'))
        title_label.pack(pady=5)
        
        content = tk.Frame(card, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True)
        
        return content
    
    def create_stat_item(self, parent, label, value, icon):
        """Create a statistics item"""
        item_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=1)
        item_frame.pack(fill=tk.X, pady=2)
        
        icon_label = tk.Label(item_frame, text=icon, bg=self.colors['bg_secondary'], 
                             fg=self.colors['accent'], font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        text_frame = tk.Frame(item_frame, bg=self.colors['bg_secondary'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        value_label = tk.Label(text_frame, text=value, bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'], font=('Segoe UI', 14, 'bold'))
        value_label.pack(anchor=tk.W)
        
        label_label = tk.Label(text_frame, text=label, bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_secondary'], font=('Segoe UI', 9))
        label_label.pack(anchor=tk.W)
        
        # Store reference for updating
        setattr(self, f"stat_{label.lower()}", value_label)
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def on_source_change(self, event):
        """Handle video source change"""
        if self.source_var.get() == "Video File":
            self.file_entry.config(state=tk.NORMAL)
        else:
            self.file_entry.config(state=tk.DISABLED)
            self.file_path_var.set("")
    
    def browse_file(self):
        """Browse for video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_video(self):
        """Load video source"""
        try:
            self.status_label.config(text="● Loading...", fg=self.colors['warning'])
            self.instruction_label.config(text="Loading video...", bg='#ffb900', fg='black')
            self.root.update()
            
            if self.source_var.get() == "Camera":
                self.video_source = 0
            else:
                video_path = self.file_path_var.get()
                if not video_path or not os.path.exists(video_path):
                    messagebox.showerror("Error", "Please select a valid video file")
                    return
                self.video_source = video_path
            
            # Release existing capture
            if self.cap:
                self.cap.release()
            
            # Initialize video capture with codec fixes for supermarket videos
            self.cap = cv2.VideoCapture(self.video_source)
            
            # Set video codec properties to fix assertion errors
            if isinstance(self.video_source, str):  # Video file
                # Try different backends for better compatibility
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
                # Force frame rate to prevent codec issues
                self.cap.set(cv2.CAP_PROP_FPS, 25)
                
            if not self.cap.isOpened():
                # Try alternative backend for problematic videos
                self.cap = cv2.VideoCapture(self.video_source, cv2.CAP_FFMPEG)
                if not self.cap.isOpened():
                    # Last resort - try DirectShow on Windows
                    self.cap = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)
                    if not self.cap.isOpened():
                        raise Exception("Failed to open video source. Please check your video file format.")
            
            # Test read a frame
            ret, test_frame = self.cap.read()
            if not ret:
                # Try to seek to beginning and read again
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, test_frame = self.cap.read()
                if not ret:
                    raise Exception("Cannot read from video source. Video may be corrupted or in unsupported format.")
            
            self.current_frame = test_frame.copy()
            self.video_loaded = True
            
            # Start video display
            self.start_video_display()
            
            # Update UI
            self.select_shelf_btn.config(state=tk.NORMAL)
            self.status_label.config(text="● Video Loaded", fg=self.colors['success'])
            self.instruction_label.config(text="✅ Video loaded! Click 'Select Areas' to define monitoring regions",
                                         bg='#107c10', fg='white')
            
            self.show_on_screen_message("✅ Video Loaded Successfully!\nReady for area selection", 
                                       color='success', duration=3000)
            
            print("Video loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
            self.status_label.config(text="● Error", fg=self.colors['error'])
            self.instruction_label.config(text="❌ Failed to load video", bg='#d13438', fg='white')
    
    def start_video_display(self):
        """Start displaying video frames"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                self.display_frame(frame)
            self.root.after(33, self.start_video_display)  # ~30 FPS
    
    def display_frame(self, frame):
        """Display frame on canvas with shelf regions"""
        if frame is None:
            return
        
        # Get canvas dimensions
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            h, w = frame.shape[:2]
            scale = min(canvas_width/w, canvas_height/h)
            new_w, new_h = int(w*scale), int(h*scale)
            
            frame_resized = cv2.resize(frame, (new_w, new_h))
            
            # Draw shelf regions
            self.draw_shelf_regions(frame_resized, scale)
            
            # Draw current selection
            self.draw_current_selection(frame_resized)
            
            # Convert to PhotoImage and display
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            self.video_canvas.delete("all")
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            self.video_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)
            self.video_canvas.image = photo
            
            # Store scaling info
            self.scale_factor = scale
            self.offset_x = x_offset
            self.offset_y = y_offset
    
    def draw_shelf_regions(self, frame, scale):
        """Draw defined shelf regions on frame with enhanced visual feedback"""
        if not self.shelf_regions:
            return
        
        current_time = time.time()
        
        for i, (corner_points, name) in enumerate(self.shelf_regions):
            # Scale corner points
            scaled_points = [(int(p[0] * scale), int(p[1] * scale)) for p in corner_points]
            pts = np.array(scaled_points, np.int32).reshape((-1, 1, 2))
            
            # Enhanced color and thickness based on monitoring results
            if self.is_monitoring and hasattr(self, 'monitoring_results') and name in self.monitoring_results:
                result = self.monitoring_results[name]
                visual_feedback = result.get('visual_feedback', {})
                
                # Get enhanced visual properties
                color = visual_feedback.get('color', (255, 255, 255))
                thickness = visual_feedback.get('thickness', 3)
                should_pulse = visual_feedback.get('should_pulse', False)
                
                # Apply pulsing effect for critical alerts
                if should_pulse:
                    pulse_factor = (np.sin(current_time * 3) + 1) / 2  # 0 to 1
                    thickness = int(thickness * (0.7 + 0.6 * pulse_factor))
                    # Pulse color intensity
                    color = tuple(int(c * (0.7 + 0.3 * pulse_factor)) for c in color)
                
            elif self.is_adjusting_points and i == self.adjusting_shelf_index:
                color = (0, 165, 255)  # Orange during adjustment
                thickness = 4
            elif self.is_monitoring:
                color = (0, 0, 255)  # Red during monitoring (no results yet)
                thickness = 3
            else:
                color = (0, 255, 0)  # Green during selection
                thickness = 2
            
            # Draw polygon
            cv2.polylines(frame, [pts], True, color, thickness)
            
            # Draw corner points with enhanced visibility
            for j, point in enumerate(scaled_points):
                if (self.is_adjusting_points and i == self.adjusting_shelf_index 
                    and j == self.adjusting_corner):
                    # Highlight current corner
                    cv2.circle(frame, point, 8, (255, 255, 0), -1)
                    cv2.circle(frame, point, 12, (255, 255, 0), 2)
                else:
                    cv2.circle(frame, point, 6, color, -1)
                    cv2.circle(frame, point, 8, (255, 255, 255), 2)
            
            # Enhanced label with monitoring information
            label_x = min(p[0] for p in scaled_points)
            label_y = min(p[1] for p in scaled_points)
            
            # Construct enhanced label text
            label_text = f"{i+1}. {name}"
            
            if self.is_monitoring and hasattr(self, 'monitoring_results') and name in self.monitoring_results:
                result = self.monitoring_results[name]
                confidence = result.get('confidence', 0)
                visual_state = result.get('visual_state', 'UNKNOWN')
                fullness = result.get('fullness_score', 0)
                
                # Multi-line enhanced information
                info_lines = [
                    label_text,
                    f"State: {visual_state}",
                    f"Conf: {confidence:.1%}",
                    f"Full: {fullness:.1%}"
                ]
            else:
                info_lines = [label_text]
            
            # Calculate background size for multi-line text
            max_width = 0
            for line in info_lines:
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                max_width = max(max_width, text_size[0])
            
            bg_height = len(info_lines) * 25 + 10
            
            # Draw enhanced background
            cv2.rectangle(frame, (label_x, label_y - bg_height), 
                         (label_x + max_width + 20, label_y - 5), color, -1)
            
            # Draw each line of information
            for idx, line in enumerate(info_lines):
                y_pos = label_y - bg_height + 20 + idx * 25
                
                # Color code different information types
                if idx == 0:  # Shelf name
                    text_color = (255, 255, 255)
                elif 'State:' in line:
                    text_color = (255, 255, 0)  # Yellow for state
                elif 'Conf:' in line:
                    # Color code confidence level
                    conf_val = result.get('confidence', 0) if 'result' in locals() else 0
                    if conf_val > 0.8:
                        text_color = (0, 0, 255)  # Red for high confidence empty
                    elif conf_val > 0.6:
                        text_color = (0, 165, 255)  # Orange
                    else:
                        text_color = (0, 255, 255)  # Yellow
                else:
                    text_color = (255, 255, 255)
                
                cv2.putText(frame, line, (label_x + 10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
    
    def draw_current_selection(self, frame):
        """Draw current selection rectangle"""
        if self.is_selecting and self.temp_selection:
            x1, y1, x2, y2 = self.temp_selection
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
            
            width, height = abs(x2 - x1), abs(y2 - y1)
            info_text = f"Selection: {width}x{height}"
            text_size = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            text_x, text_y = min(x1, x2), min(y1, y2) - 10
            if text_y < 30:
                text_y = max(y1, y2) + 25
            
            cv2.rectangle(frame, (text_x, text_y - 20), 
                         (text_x + text_size[0] + 10, text_y + 5), (0, 255, 255), -1)
            cv2.putText(frame, info_text, (text_x + 5, text_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    def toggle_selection(self):
        """Toggle area selection mode"""
        if not self.video_loaded:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        if not self.is_selecting:
            # Start selection
            self.is_selecting = True
            self.select_shelf_btn.config(text="✅ Done Selecting", bg=self.colors['success'])
            self.instruction_label.config(text="🎯 Click and drag to select areas. Click 'Done' when finished.",
                                         bg='#ffb900', fg='black')
            self.status_label.config(text="● Selecting Areas", fg=self.colors['warning'])
        else:
            # Stop selection
            self.is_selecting = False
            self.select_shelf_btn.config(text="🎯 Select Areas", bg=self.colors['warning'])
            self.instruction_label.config(text="✅ Selection completed! Click 'Start Monitoring' to begin.",
                                         bg='#107c10', fg='white')
            self.status_label.config(text="● Areas Selected", fg=self.colors['success'])
            
            if len(self.shelf_regions) > 0:
                self.monitor_btn.config(state=tk.NORMAL)
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.video_loaded:
            return
        
        if self.is_adjusting_points:
            self.handle_corner_click(event)
        elif self.is_selecting:
            self.start_selection(event)
    
    def start_selection(self, event):
        """Start area selection"""
        if not hasattr(self, 'scale_factor'):
            return
        
        # Convert to frame coordinates
        x = int((event.x - self.offset_x) / self.scale_factor)
        y = int((event.y - self.offset_y) / self.scale_factor)
        
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            x = max(0, min(x, w))
            y = max(0, min(y, h))
        
        self.selection_start = (x, y)
        print(f"Selection started at: ({x}, {y})")
    
    def on_canvas_drag(self, event):
        """Handle canvas drag for selection"""
        if not self.is_selecting or not self.selection_start:
            return
        
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        x_canvas = max(0, min(event.x, canvas_width))
        y_canvas = max(0, min(event.y, canvas_height))
        
        x1, y1 = self.selection_start
        x1_canvas = int(x1 * self.scale_factor + self.offset_x)
        y1_canvas = int(y1 * self.scale_factor + self.offset_y)
        
        self.temp_selection = (x1_canvas, y1_canvas, x_canvas, y_canvas)
        
        if hasattr(self, 'current_frame'):
            self.display_frame(self.current_frame)
    
    def on_canvas_release(self, event):
        """Handle canvas release to complete selection"""
        if not self.is_selecting or not self.selection_start:
            return
        
        if not hasattr(self, 'scale_factor'):
            return
        
        # Convert to frame coordinates
        x2 = int((event.x - self.offset_x) / self.scale_factor)
        y2 = int((event.y - self.offset_y) / self.scale_factor)
        
        x1, y1 = self.selection_start
        
        if hasattr(self, 'current_frame'):
            h, w = self.current_frame.shape[:2]
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
        
        # Create rectangle
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        
        if w > 20 and h > 20:
            # Get area name
            name = self.get_area_name()
            if name:
                # Convert to 4 corner points
                corner_points = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
                self.shelf_regions.append((corner_points, name))
                self.update_shelf_list()
                
                # Show corner adjustment dialog
                self.show_corner_adjustment_dialog(len(self.shelf_regions) - 1, name)
        else:
            self.show_on_screen_message("❌ Selection too small!", color='error', duration=2000)
        
        # Clear selection
        self.temp_selection = None
        self.selection_start = None
    
    def show_corner_adjustment_dialog(self, shelf_index, shelf_name):
        """Show dialog for corner adjustment"""
        result = messagebox.askyesno(
            "Adjust Corner Points", 
            f"Do you want to adjust the 4 corner points of '{shelf_name}' for perfect shape?\n\n"
            "Click 'Yes' to adjust corners manually\n"
            "Click 'No' to keep rectangle shape"
        )
        
        if result:
            self.start_corner_adjustment(shelf_index)
        else:
            self.show_on_screen_message(f"✅ Area '{shelf_name}' Added!", color='success', duration=2000)
    
    def start_corner_adjustment(self, shelf_index):
        """Start corner adjustment mode"""
        self.is_adjusting_points = True
        self.adjusting_shelf_index = shelf_index
        self.adjusting_corner = 0
        
        corner_points, name = self.shelf_regions[shelf_index]
        
        self.instruction_label.config(
            text=f"🔧 Click to position corner {self.adjusting_corner + 1}/4 of '{name}'",
            bg='#ff6600', fg='white'
        )
        self.status_label.config(text="● Adjusting Corners", fg=self.colors['warning'])
        
        self.show_on_screen_message(f"🔧 Adjusting '{name}'\nClick corner {self.adjusting_corner + 1}/4",
                                   color='warning', duration=3000)
    
    def handle_corner_click(self, event):
        """Handle corner adjustment clicks"""
        if not hasattr(self, 'scale_factor'):
            return
        
        # Convert to frame coordinates
        x = int((event.x - self.offset_x) / self.scale_factor)
        y = int((event.y - self.offset_y) / self.scale_factor)
        
        if hasattr(self, 'current_frame'):
            h, w = self.current_frame.shape[:2]
            x = max(0, min(x, w))
            y = max(0, min(y, h))
        
        # Update corner
        corner_points, name = self.shelf_regions[self.adjusting_shelf_index]
        corner_points[self.adjusting_corner] = (x, y)
        
        self.adjusting_corner += 1
        
        if self.adjusting_corner < 4:
            # Continue with next corner
            self.instruction_label.config(
                text=f"🔧 Click to position corner {self.adjusting_corner + 1}/4 of '{name}'",
                bg='#ff6600', fg='white'
            )
            self.show_on_screen_message(f"🔧 Corner {self.adjusting_corner}/4 done!\nClick corner {self.adjusting_corner + 1}/4",
                                       color='warning', duration=2000)
        else:
            # Finished
            self.finish_corner_adjustment()
    
    def finish_corner_adjustment(self):
        """Finish corner adjustment"""
        corner_points, name = self.shelf_regions[self.adjusting_shelf_index]
        
        self.is_adjusting_points = False
        self.adjusting_shelf_index = -1
        self.adjusting_corner = -1
        
        self.instruction_label.config(
            text=f"✅ Perfect! '{name}' shape adjusted. Continue selecting or click 'Done'",
            bg='#107c10', fg='white'
        )
        self.status_label.config(text="● Selecting Areas", fg=self.colors['warning'])
        
        self.show_on_screen_message(f"✅ Perfect Shape!\n'{name}' corners adjusted", 
                                   color='success', duration=3000)
    
    def get_area_name(self):
        """Get area name from user"""
        dialog = AreaNameDialog(self.root)
        self.root.wait_window(dialog.dialog)
        return dialog.result
    
    def update_shelf_list(self):
        """Update shelf list display"""
        self.shelf_listbox.delete(0, tk.END)
        for i, (corner_points, name) in enumerate(self.shelf_regions):
            xs = [p[0] for p in corner_points]
            ys = [p[1] for p in corner_points]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            self.shelf_listbox.insert(tk.END, f"{i+1}. {name} ({w:.0f}x{h:.0f})")
        
        # Update stats
        self.stat_areas.config(text=str(len(self.shelf_regions)))
    
    def delete_shelf(self):
        """Delete selected shelf"""
        selection = self.shelf_listbox.curselection()
        if selection:
            index = selection[0]
            del self.shelf_regions[index]
            self.update_shelf_list()
            if len(self.shelf_regions) == 0:
                self.monitor_btn.config(state=tk.DISABLED)
    
    def clear_shelves(self):
        """Clear all shelves"""
        if messagebox.askyesno("Confirm", "Clear all defined areas?"):
            self.shelf_regions.clear()
            self.update_shelf_list()
            self.monitor_btn.config(state=tk.DISABLED)
    
    def toggle_monitoring(self):
        """Toggle monitoring state"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring"""
        if not self.shelf_regions:
            messagebox.showwarning("Warning", "Please define at least one area")
            return
        
        try:
            # Initialize detector
            from improved_yolo_detector import ImprovedYOLODetector
            self.detector = ImprovedYOLODetector(sensitivity=self.sensitivity_var.get())
            
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Update UI
            self.monitor_btn.config(text="⏹️ Stop Monitoring", bg=self.colors['error'])
            self.status_label.config(text="● Monitoring Active", fg=self.colors['success'])
            self.instruction_label.config(text="🔍 MONITORING: Analyzing areas for empty sections...",
                                         bg='#107c10', fg='white')
            self.select_shelf_btn.config(state=tk.DISABLED)
            
            self.show_on_screen_message(f"🔍 Monitoring Started!\nWatching {len(self.shelf_regions)} areas",
                                       color='info', duration=3000)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        
        # Update UI
        self.monitor_btn.config(text="▶️ Start Monitoring", bg=self.colors['success'])
        self.status_label.config(text="● Monitoring Stopped", fg=self.colors['warning'])
        self.instruction_label.config(text="Monitoring stopped. Click 'Start Monitoring' to resume.",
                                     bg='#2d2d2d', fg='white')
        self.select_shelf_btn.config(state=tk.NORMAL)
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        frame_count = 0
        alert_count = 0
        start_time = time.time()
        
        while self.is_monitoring and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame_count += 1
            current_time = time.time()
            self.current_frame = frame.copy()
            
            # Update detector sensitivity
            if hasattr(self, 'detector'):
                self.detector.update_sensitivity(self.sensitivity_var.get())
            
            empty_shelves = 0
            processed_frame = frame.copy()
            
            # Process each shelf region
            for i, (corner_points, name) in enumerate(self.shelf_regions):
                try:
                    # Create bounding rectangle
                    xs = [p[0] for p in corner_points]
                    ys = [p[1] for p in corner_points]
                    x, y = min(xs), min(ys)
                    w, h = max(xs) - x, max(ys) - y
                    
                    # Bounds check
                    frame_h, frame_w = frame.shape[:2]
                    x = max(0, min(x, frame_w - 1))
                    y = max(0, min(y, frame_h - 1))
                    w = min(w, frame_w - x)
                    h = min(h, frame_h - y)
                    
                    if w <= 0 or h <= 0:
                        continue
                    
                    # Extract ROI
                    roi = frame[y:y+h, x:x+w]
                    
                    # Analyze with detector
                    if hasattr(self, 'detector'):
                        result = self.detector.analyze_shelf_region(roi, name, current_time)
                        is_empty = result['is_empty']
                        confidence = result['confidence']
                        should_alert = result['should_alert']
                        
                        # Draw visualization
                        pts = np.array(corner_points, np.int32)
                        if is_empty:
                            empty_shelves += 1
                            cv2.polylines(processed_frame, [pts], True, (0, 0, 255), 4)
                            
                            if should_alert:
                                alert_count += 1
                                alert_msg = f"🚨 EMPTY SHELF ALERT!\nShelf: {name}\nConfidence: {confidence:.0%}\nTime: {datetime.now().strftime('%H:%M:%S')}"
                                self.alert_queue.put(alert_msg)
                                
                                # Show on-screen alert
                                self.root.after(0, lambda n=name, c=confidence: 
                                               self.show_on_screen_message(
                                                   f"🚨 SHELF EMPTY!\n'{n}' ({c:.0%} confidence)",
                                                   color='alert', duration=4000
                                               ))
                        else:
                            cv2.polylines(processed_frame, [pts], True, (0, 255, 0), 3)
                        
                        # Draw status text
                        status_text = f"{'EMPTY' if is_empty else 'OK'}: {name}"
                        conf_text = f"Conf: {confidence:.0%}"
                        
                        cv2.rectangle(processed_frame, (x, y-40), (x + 200, y-5), 
                                     (0, 0, 255) if is_empty else (0, 255, 0), -1)
                        cv2.putText(processed_frame, status_text, (x+5, y-25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.putText(processed_frame, conf_text, (x+5, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                except Exception as e:
                    print(f"Error processing {name}: {e}")
            
            # Add overlay info
            self.add_monitoring_overlay(processed_frame, frame_count, start_time, empty_shelves, alert_count)
            
            # Update UI stats
            fps = frame_count / max(current_time - start_time, 1)
            self.root.after(0, lambda: self.update_monitoring_stats(empty_shelves, alert_count, int(fps)))
            
            # Queue frame for display
            try:
                if not self.frame_queue.full():
                    self.frame_queue.put(processed_frame)
            except:
                pass
            
            time.sleep(0.03)  # ~33 FPS
    
    def add_monitoring_overlay(self, frame, frame_count, start_time, empty_shelves, alert_count):
        """Add monitoring info overlay"""
        h, w = frame.shape[:2]
        current_time = time.time()
        fps = frame_count / max(current_time - start_time, 1)
        
        # Overlay background
        overlay_w, overlay_h = 220, 140
        cv2.rectangle(frame, (w-overlay_w-10, 10), (w-10, 10+overlay_h), (30, 30, 30), -1)
        cv2.rectangle(frame, (w-overlay_w-10, 10), (w-10, 10+overlay_h), (100, 149, 237), 3)
        
        # Info lines
        info_lines = [
            "MONITORING STATUS",
            f"Frame: {frame_count}",
            f"FPS: {fps:.1f}",
            f"Areas: {len(self.shelf_regions)}",
            f"Empty: {empty_shelves}",
            f"Alerts: {alert_count}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        for i, line in enumerate(info_lines):
            y_pos = 30 + i * 18
            font_scale = 0.6 if i == 0 else 0.5
            font_weight = 2 if i == 0 else 1
            color = (255, 255, 255)
            cv2.putText(frame, line, (w-overlay_w+5, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_weight)
    
    def update_monitoring_stats(self, empty_shelves, alert_count, fps):
        """Update monitoring statistics with enhanced feedback"""
        self.stat_empty.config(text=str(empty_shelves))
        self.stat_alerts.config(text=str(alert_count))
        self.stat_fps.config(text=str(fps))
        
        # Update enhanced displays
        self.update_detection_status()
        self.update_method_scores()
    
    def update_detection_status(self):
        """Update the real-time detection status display"""
        try:
            # Clear previous display
            for widget in self.detection_display.winfo_children():
                widget.destroy()
            
            if not hasattr(self, 'monitoring_results') or not self.monitoring_results:
                tk.Label(self.detection_display, text="No detection data available", 
                        bg=self.colors['bg_card'], fg=self.colors['text_secondary']).pack()
                return
            
            # Create status display for each shelf
            for shelf_name, result in self.monitoring_results.items():
                shelf_frame = tk.Frame(self.detection_display, bg=self.colors['bg_secondary'], 
                                     relief='raised', bd=1)
                shelf_frame.pack(fill=tk.X, padx=2, pady=1)
                
                # Shelf name and state
                header_frame = tk.Frame(shelf_frame, bg=self.colors['bg_secondary'])
                header_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Visual state indicator
                visual_state = result.get('visual_state', 'UNKNOWN')
                state_colors = {
                    'CRITICALLY_EMPTY': '#ff0000',
                    'MOSTLY_EMPTY': '#ff4500', 
                    'PARTIALLY_EMPTY': '#ffa500',
                    'LOW_STOCK': '#ffff00',
                    'WELL_STOCKED': '#00ff00',
                    'UNCERTAIN': '#808080'
                }
                
                state_color = state_colors.get(visual_state, '#808080')
                
                # State indicator circle
                indicator = tk.Label(header_frame, text="●", fg=state_color, 
                                   bg=self.colors['bg_secondary'], font=('Segoe UI', 16))
                indicator.pack(side=tk.LEFT)
                
                # Shelf info
                tk.Label(header_frame, text=f"{shelf_name}: {visual_state}", 
                        bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                        font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
                
                # Confidence and scores
                info_frame = tk.Frame(shelf_frame, bg=self.colors['bg_secondary'])
                info_frame.pack(fill=tk.X, padx=15, pady=2)
                
                confidence = result.get('confidence', 0)
                fullness = result.get('fullness_score', 0)
                trend = result.get('trend', 'UNKNOWN')
                
                tk.Label(info_frame, text=f"Confidence: {confidence:.1%} | Fullness: {fullness:.1%} | Trend: {trend}",
                        bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                        font=('Segoe UI', 8)).pack()
                
        except Exception as e:
            print(f"Detection status update error: {e}")
    
    def update_method_scores(self):
        """Update the method scores display"""
        try:
            # Clear previous display
            for widget in self.scores_display.winfo_children():
                widget.destroy()
            
            if not hasattr(self, 'monitoring_results') or not self.monitoring_results:
                tk.Label(self.scores_display, text="No method score data available", 
                        bg=self.colors['bg_card'], fg=self.colors['text_secondary']).pack()
                return
            
            # Calculate average method scores
            all_method_scores = {}
            for result in self.monitoring_results.values():
                method_scores = result.get('method_scores', {})
                for method, score in method_scores.items():
                    if method not in all_method_scores:
                        all_method_scores[method] = []
                    all_method_scores[method].append(score)
            
            # Display average scores
            if all_method_scores:
                tk.Label(self.scores_display, text="Average Detection Method Scores:", 
                        bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                        font=('Segoe UI', 9, 'bold')).pack(pady=(5, 10))
                
                for method, scores in all_method_scores.items():
                    avg_score = np.mean(scores)
                    
                    method_frame = tk.Frame(self.scores_display, bg=self.colors['bg_secondary'])
                    method_frame.pack(fill=tk.X, padx=5, pady=1)
                    
                    # Method name
                    tk.Label(method_frame, text=f"{method.replace('_', ' ').title()}:", 
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            font=('Segoe UI', 8), width=15, anchor='w').pack(side=tk.LEFT)
                    
                    # Score bar
                    bar_frame = tk.Frame(method_frame, bg=self.colors['bg_secondary'])
                    bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
                    
                    # Progress bar simulation
                    bar_width = int(avg_score * 100)
                    bar_color = '#00ff00' if avg_score > 0.7 else '#ffff00' if avg_score > 0.4 else '#ff0000'
                    
                    tk.Label(bar_frame, text=f"{'█' * (bar_width // 5)}", 
                            fg=bar_color, bg=self.colors['bg_secondary'],
                            font=('Segoe UI', 8)).pack(side=tk.LEFT)
                    
                    # Score value
                    tk.Label(method_frame, text=f"{avg_score:.2f}", 
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            font=('Segoe UI', 8, 'bold')).pack(side=tk.RIGHT)
                            
        except Exception as e:
            print(f"Method scores update error: {e}")
    
    def show_on_screen_message(self, message, color='info', duration=3000):
        """Show on-screen message"""
        self.message_id_counter += 1
        message_id = self.message_id_counter
        
        color_schemes = {
            'success': {'bg': '#107c10', 'fg': 'white'},
            'error': {'bg': '#d13438', 'fg': 'white'},
            'warning': {'bg': '#ffb900', 'fg': 'black'},
            'info': {'bg': '#0078d4', 'fg': 'white'},
            'alert': {'bg': '#ff4444', 'fg': 'white'}
        }
        
        scheme = color_schemes.get(color, color_schemes['info'])
        
        # Create message frame
        message_frame = tk.Frame(self.video_canvas, bg=scheme['bg'], relief='raised', bd=3)
        
        # Icon
        icons = {'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️', 'alert': '🚨'}
        icon = icons.get(color, 'ℹ️')
        
        content_frame = tk.Frame(message_frame, bg=scheme['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        icon_label = tk.Label(content_frame, text=icon, bg=scheme['bg'], fg=scheme['fg'], font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        text_label = tk.Label(content_frame, text=message, bg=scheme['bg'], fg=scheme['fg'],
                            font=('Segoe UI', 11, 'bold'), justify=tk.LEFT)
        text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Position message
        canvas_width = self.video_canvas.winfo_width()
        message_width = 400
        x_pos = (canvas_width - message_width) // 2
        y_pos = 20 + len(self.on_screen_messages) * 90
        
        message_window = self.video_canvas.create_window(x_pos, y_pos, window=message_frame, 
                                                        width=message_width, height=70, anchor=tk.NW)
        
        message_info = {
            'id': message_id,
            'frame': message_frame,
            'window': message_window,
            'start_time': time.time(),
            'duration': duration / 1000.0
        }
        
        self.on_screen_messages.append(message_info)
    
    def update_on_screen_messages(self):
        """Update and remove expired messages"""
        current_time = time.time()
        messages_to_remove = []
        
        for message_info in self.on_screen_messages:
            if current_time - message_info['start_time'] > message_info['duration']:
                messages_to_remove.append(message_info)
        
        for message_info in messages_to_remove:
            try:
                self.video_canvas.delete(message_info['window'])
                message_info['frame'].destroy()
                self.on_screen_messages.remove(message_info)
            except:
                pass
        
        self.root.after(100, self.update_on_screen_messages)
    
    def update_display(self):
        """Update display with processed frames"""
        try:
            if not self.frame_queue.empty():
                processed_frame = self.frame_queue.get_nowait()
                if self.is_monitoring:
                    self.display_frame(processed_frame)
        except:
            pass
        
        self.root.after(50, self.update_display)
    
    def update_alerts(self):
        """Update alerts display"""
        new_alerts = []
        while not self.alert_queue.empty():
            try:
                alert = self.alert_queue.get_nowait()
                new_alerts.append(alert)
            except:
                break
        
        if new_alerts:
            for alert in new_alerts:
                self.alert_text.insert(tk.END, alert + "\n" + "="*40 + "\n")
                self.alert_text.see(tk.END)
                
                if self.sound_var.get():
                    self.play_alert_sound()
        
        self.root.after(1000, self.update_alerts)
    
    def play_alert_sound(self):
        """Play alert sound"""
        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            pass
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        try:
            self.is_monitoring = False
            if self.cap:
                self.cap.release()
            self.root.destroy()
        except:
            pass


class AreaNameDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Area Name")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#2d2d2d')
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create content
        main_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Label
        label = tk.Label(main_frame, text="Enter area name:", 
                        bg='#2d2d2d', fg='white', font=('Segoe UI', 12))
        label.pack(pady=(0, 10))
        
        # Entry
        self.entry = tk.Entry(main_frame, font=('Segoe UI', 12), width=25)
        self.entry.pack(pady=(0, 20))
        self.entry.focus()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2d2d2d')
        button_frame.pack()
        
        ok_btn = tk.Button(button_frame, text="OK", command=self.ok_clicked,
                          bg='#0078d4', fg='white', font=('Segoe UI', 10, 'bold'),
                          relief='flat', padx=20, pady=5)
        ok_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                              bg='#d13438', fg='white', font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT)
        
        # Bind keys
        self.entry.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        self.result = self.entry.get().strip()
        if not self.result:
            self.result = f"Area_{int(time.time() % 10000)}"
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


if __name__ == "__main__":
    app = ModernShelfMonitoringApp()
    app.run()
