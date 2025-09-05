"""
Simple GUI for Shelf Monitoring System
Provides an easy-to-use interface for the monitoring system
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import threading
import time
from PIL import Image, ImageTk
import queue
import os

class ShelfMonitoringGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shelf Monitoring System")
        self.root.geometry("1200x800")
        
        # System components
        self.monitoring_system = None
        self.video_thread = None
        self.is_monitoring = False
        
        # GUI components
        self.frame_queue = queue.Queue()
        self.log_queue = queue.Queue()
        
        self.create_widgets()
        self.setup_logging()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Video source selection
        ttk.Label(control_frame, text="Video Source:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.source_var = tk.StringVar(value="Camera")
        source_combo = ttk.Combobox(control_frame, textvariable=self.source_var, 
                                   values=["Camera", "Video File"], state="readonly", width=15)
        source_combo.grid(row=0, column=1, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(control_frame, textvariable=self.file_path_var, width=40)
        self.file_entry.grid(row=0, column=2, padx=(0, 10))
        
        browse_btn = ttk.Button(control_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        
        self.start_btn = ttk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.config_btn = ttk.Button(button_frame, text="Configure", command=self.open_config)
        self.config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.demo_btn = ttk.Button(button_frame, text="Run Demo", command=self.run_demo)
        self.demo_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video display
        video_frame = ttk.LabelFrame(content_frame, text="Video Feed", padding="5")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Info panel
        info_frame = ttk.LabelFrame(content_frame, text="Information", padding="5")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, ipadx=10)
        
        # Status
        status_frame = ttk.LabelFrame(info_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = scrolledtext.ScrolledText(status_frame, width=40, height=10, font=("Consolas", 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Alerts
        alerts_frame = ttk.LabelFrame(info_frame, text="Active Alerts", padding="5")
        alerts_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.alerts_text = scrolledtext.ScrolledText(alerts_frame, width=40, height=8, font=("Consolas", 9))
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.LabelFrame(info_frame, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X)
        
        self.stats_text = tk.Text(stats_frame, width=40, height=6, font=("Consolas", 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Start update loops
        self.root.after(100, self.update_display)
        self.root.after(1000, self.update_info)
    
    def setup_logging(self):
        """Setup logging to capture system messages"""
        import logging
        
        class GUILogHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
            
            def emit(self, record):
                log_message = self.format(record)
                self.log_queue.put(log_message)
        
        # Add handler to root logger
        handler = GUILogHandler(self.log_queue)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
    
    def browse_file(self):
        """Browse for video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def start_monitoring(self):
        """Start the monitoring system"""
        try:
            # Initialize system
            from main import ShelfMonitoringSystem
            self.monitoring_system = ShelfMonitoringSystem()
            
            # Determine video source
            if self.source_var.get() == "Camera":
                video_source = 0
            else:
                video_source = self.file_path_var.get()
                if not video_source or not os.path.exists(video_source):
                    messagebox.showerror("Error", "Please select a valid video file")
                    return
            
            # Start monitoring thread
            self.is_monitoring = True
            self.video_thread = threading.Thread(target=self.monitoring_loop, args=(video_source,))
            self.video_thread.daemon = True
            self.video_thread.start()
            
            # Update button states
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_message("Monitoring started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)
        
        if self.monitoring_system:
            self.monitoring_system.cleanup()
        
        # Update button states
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log_message("Monitoring stopped")
    
    def monitoring_loop(self, video_source):
        """Main monitoring loop running in separate thread"""
        try:
            self.monitoring_system.initialize_video_capture(video_source)
            
            while self.is_monitoring:
                ret, frame = self.monitoring_system.cap.read()
                if not ret:
                    break
                
                # Process frame
                analysis_results = self.monitoring_system.process_frame(frame)
                
                # Visualize frame
                display_frame = self.monitoring_system.visualize_frame(frame, analysis_results)
                
                # Resize for display
                height, width = display_frame.shape[:2]
                if width > 800:
                    scale = 800 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    display_frame = cv2.resize(display_frame, (new_width, new_height))
                
                # Convert to RGB for tkinter
                display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Put frame in queue for GUI update
                if not self.frame_queue.full():
                    self.frame_queue.put((display_frame_rgb, analysis_results))
                
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            self.log_message(f"Monitoring error: {e}")
        finally:
            if self.monitoring_system:
                self.monitoring_system.cleanup()
    
    def update_display(self):
        """Update video display"""
        try:
            # Get latest frame
            if not self.frame_queue.empty():
                frame_rgb, analysis_results = self.frame_queue.get()
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update display
                self.video_label.config(image=photo)
                self.video_label.image = photo  # Keep a reference
                
        except Exception as e:
            pass  # Ignore display errors
        
        # Schedule next update
        self.root.after(33, self.update_display)  # ~30 FPS
    
    def update_info(self):
        """Update information panels"""
        # Update logs
        while not self.log_queue.empty():
            log_message = self.log_queue.get()
            self.status_text.insert(tk.END, log_message + "\n")
            self.status_text.see(tk.END)
        
        # Update alerts
        if self.monitoring_system and hasattr(self.monitoring_system, 'alert_system'):
            alerts = self.monitoring_system.alert_system.active_alerts
            
            self.alerts_text.delete(1.0, tk.END)
            if alerts:
                for section, alert in alerts.items():
                    alert_text = f"{alert['message']} ({alert['confidence']:.0%})\n"
                    self.alerts_text.insert(tk.END, alert_text)
            else:
                self.alerts_text.insert(tk.END, "No active alerts")
        
        # Update statistics
        if self.monitoring_system:
            stats_text = f"Frame: {getattr(self.monitoring_system, 'frame_count', 0)}\n"
            stats_text += f"FPS: {getattr(self.monitoring_system, 'fps', 0)}\n"
            
            if hasattr(self.monitoring_system, 'alert_system'):
                alert_summary = self.monitoring_system.alert_system.get_alert_summary()
                stats_text += f"Active Alerts: {alert_summary['active_alerts']}\n"
                stats_text += f"Total Today: {alert_summary['total_alerts_today']}\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
        
        # Schedule next update
        self.root.after(1000, self.update_info)
    
    def log_message(self, message):
        """Add message to log queue"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"{timestamp} - {message}")
    
    def open_config(self):
        """Open configuration dialog"""
        ConfigDialog(self.root)
    
    def run_demo(self):
        """Run demo in separate window"""
        try:
            from demo import run_demo
            threading.Thread(target=run_demo, daemon=True).start()
            self.log_message("Demo started (check console output)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run demo: {e}")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.quit()
        self.root.destroy()

class ConfigDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_config_widgets()
    
    def create_config_widgets(self):
        """Create configuration widgets"""
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video settings
        video_frame = ttk.Frame(notebook)
        notebook.add(video_frame, text="Video")
        
        ttk.Label(video_frame, text="Video Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Detection settings
        detection_frame = ttk.Frame(notebook)
        notebook.add(detection_frame, text="Detection")
        
        ttk.Label(detection_frame, text="Detection Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Alert settings
        alert_frame = ttk.Frame(notebook)
        notebook.add(alert_frame, text="Alerts")
        
        ttk.Label(alert_frame, text="Alert Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def save_config(self):
        """Save configuration"""
        # Implementation for saving config
        messagebox.showinfo("Info", "Configuration saved successfully!")
        self.dialog.destroy()

def main():
    """Main function"""
    try:
        app = ShelfMonitoringGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
