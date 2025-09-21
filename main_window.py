"""
Main Window for JARVIS Assistant
Futuristic GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import numpy as np
from typing import Optional, Dict, Any

from core.jarvis_core import JarvisCore
from config.config import config
from utils.logger import get_logger, JarvisLogHandler

# Set CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisMainWindow:
    """Main JARVIS GUI Window"""
    
    def __init__(self, root: tk.Tk, jarvis_core: JarvisCore):
        self.root = root
        self.jarvis_core = jarvis_core
        self.logger = get_logger(__name__)
        
        # Window configuration
        self.setup_window()
        
        # GUI Components
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # JARVIS Integration
        self.setup_jarvis_callbacks()
        
        # Start status updates
        self.start_status_updates()
        
        # Animation variables
        self.animation_frame = 0
        self.is_animating = False
        
        self.logger.info("JARVIS GUI initialized")
    
    def setup_window(self):
        """Configure main window"""
        self.root.title("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        self.root.geometry(config.get('ui.window_size', '1200x800'))
        self.root.configure(bg='#0A0A0A')
        
        # Window properties
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('assets/jarvis_icon.ico')
        except:
            pass
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Setup custom styles"""
        self.accent_color = config.get('ui.accent_color', '#00D4FF')
        self.bg_color = config.get('ui.background_color', '#0A0A0A')
        self.text_color = config.get('ui.text_color', '#FFFFFF')
        
        # Custom fonts
        self.title_font = ('Orbitron', 24, 'bold')
        self.header_font = ('Orbitron', 14, 'bold')
        self.normal_font = ('Consolas', 10)
        self.small_font = ('Consolas', 8)
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
        # Control panel
        self.create_control_panel()
    
    def create_header(self):
        """Create header section"""
        self.header_frame = ctk.CTkFrame(
            self.main_frame,
            height=100,
            fg_color='#111111',
            corner_radius=10
        )
        
        # JARVIS title with animation effect
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="J.A.R.V.I.S",
            font=self.title_font,
            text_color=self.accent_color
        )
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Just A Rather Very Intelligent System",
            font=('Orbitron', 12),
            text_color='#888888'
        )
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="●",
            font=('Arial', 20),
            text_color='#00FF00'
        )
        
        # API status
        self.api_status_label = ctk.CTkLabel(
            self.header_frame,
            text="API: Disconnected",
            font=self.small_font,
            text_color='#FF4444'
        )
    
    def create_main_content(self):
        """Create main content area"""
        # Content notebook
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Chat tab
        self.chat_frame = ctk.CTkFrame(self.notebook, fg_color='#111111')
        self.notebook.add(self.chat_frame, text="Chat")
        self.create_chat_interface()
        
        # Camera tab
        self.camera_frame = ctk.CTkFrame(self.notebook, fg_color='#111111')
        self.notebook.add(self.camera_frame, text="Camera")
        self.create_camera_interface()
        
        # System tab
        self.system_frame = ctk.CTkFrame(self.notebook, fg_color='#111111')
        self.notebook.add(self.system_frame, text="System")
        self.create_system_interface()
        
        # Logs tab
        self.logs_frame = ctk.CTkFrame(self.notebook, fg_color='#111111')
        self.notebook.add(self.logs_frame, text="Logs")
        self.create_logs_interface()
        
        # Settings tab
        self.settings_frame = ctk.CTkFrame(self.notebook, fg_color='#111111')
        self.notebook.add(self.settings_frame, text="Settings")
        self.create_settings_interface()
    
    def create_chat_interface(self):
        """Create chat interface"""
        # Chat display
        self.chat_display = tk.Text(
            self.chat_frame,
            bg='#000000',
            fg=self.text_color,
            font=self.normal_font,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        
        # Scrollbar for chat
        self.chat_scrollbar = ttk.Scrollbar(
            self.chat_frame,
            orient="vertical",
            command=self.chat_display.yview
        )
        self.chat_display.configure(yscrollcommand=self.chat_scrollbar.set)
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color='transparent')
        
        # Text input
        self.text_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message or press 'Listen' to use voice...",
            font=self.normal_font,
            height=40
        )
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.send_message,
            fg_color=self.accent_color,
            hover_color='#0099CC',
            width=80
        )
        
        # Voice button
        self.voice_button = ctk.CTkButton(
            self.input_frame,
            text="🎤 Listen",
            command=self.start_voice_input,
            fg_color='#FF6B35',
            hover_color='#CC5428',
            width=100
        )
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.input_frame,
            text="Clear",
            command=self.clear_chat,
            fg_color='#666666',
            hover_color='#555555',
            width=80
        )
        
        # Bind Enter key
        self.text_input.bind("<Return>", lambda e: self.send_message())
    
    def create_camera_interface(self):
        """Create camera interface"""
        # Camera controls
        self.camera_controls = ctk.CTkFrame(self.camera_frame, fg_color='transparent')
        
        # Camera toggle
        self.camera_toggle = ctk.CTkButton(
            self.camera_controls,
            text="Start Camera",
            command=self.toggle_camera,
            fg_color='#00AA00',
            hover_color='#008800'
        )
        
        # Take photo button
        self.photo_button = ctk.CTkButton(
            self.camera_controls,
            text="📷 Photo",
            command=self.take_photo,
            fg_color=self.accent_color,
            hover_color='#0099CC',
            state='disabled'
        )
        
        # Camera display
        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="Camera Feed\n(Click 'Start Camera' to begin)",
            fg_color='#222222',
            corner_radius=10,
            height=400
        )
    
    def create_system_interface(self):
        """Create system monitoring interface"""
        # System info display
        self.system_info = tk.Text(
            self.system_frame,
            bg='#000000',
            fg=self.text_color,
            font=self.normal_font,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=15
        )
        
        # System controls
        self.system_controls = ctk.CTkFrame(self.system_frame, fg_color='transparent')
        
        # Volume controls
        self.volume_frame = ctk.CTkFrame(self.system_controls, fg_color='#222222')
        
        ctk.CTkLabel(
            self.volume_frame,
            text="Volume Control",
            font=self.header_font
        ).pack(pady=5)
        
        volume_buttons_frame = ctk.CTkFrame(self.volume_frame, fg_color='transparent')
        
        ctk.CTkButton(
            volume_buttons_frame,
            text="🔊 +",
            command=lambda: self.jarvis_core.system_controller.increase_volume(),
            width=60
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            volume_buttons_frame,
            text="🔉 -",
            command=lambda: self.jarvis_core.system_controller.decrease_volume(),
            width=60
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            volume_buttons_frame,
            text="🔇",
            command=lambda: self.jarvis_core.system_controller.mute_volume(),
            width=60
        ).pack(side=tk.LEFT, padx=5)
        
        volume_buttons_frame.pack(pady=5)
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.system_controls,
            text="🔄 Refresh Info",
            command=self.update_system_info,
            fg_color=self.accent_color
        )
    
    def create_logs_interface(self):
        """Create logs interface"""
        # Logs display
        self.logs_display = tk.Text(
            self.logs_frame,
            bg='#000000',
            fg=self.text_color,
            font=self.small_font,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=25
        )
        
        # Logs scrollbar
        self.logs_scrollbar = ttk.Scrollbar(
            self.logs_frame,
            orient="vertical",
            command=self.logs_display.yview
        )
        self.logs_display.configure(yscrollcommand=self.logs_scrollbar.set)
        
        # Setup log handler
        self.log_handler = JarvisLogHandler(callback=self.add_log_entry)
        get_logger('jarvis').addHandler(self.log_handler)
    
    def create_settings_interface(self):
        """Create settings interface"""
        # Settings scroll frame
        self.settings_scroll = ctk.CTkScrollableFrame(self.settings_frame)
        
        # API Settings
        self.api_frame = ctk.CTkFrame(self.settings_scroll, fg_color='#222222')
        
        ctk.CTkLabel(
            self.api_frame,
            text="OpenRouter API Settings",
            font=self.header_font
        ).pack(pady=10)
        
        # API Key
        ctk.CTkLabel(self.api_frame, text="API Key:").pack(anchor='w', padx=10)
        self.api_key_entry = ctk.CTkEntry(
            self.api_frame,
            placeholder_text="Enter your OpenRouter API key",
            show="*",
            width=400
        )
        self.api_key_entry.pack(pady=5, padx=10, fill='x')
        
        # Model selection
        ctk.CTkLabel(self.api_frame, text="Model:").pack(anchor='w', padx=10, pady=(10,0))
        self.model_var = tk.StringVar(value=config.get('openrouter.model', 'anthropic/claude-3-sonnet'))
        self.model_entry = ctk.CTkEntry(
            self.api_frame,
            textvariable=self.model_var,
            width=400
        )
        self.model_entry.pack(pady=5, padx=10, fill='x')
        
        # Save API settings button
        ctk.CTkButton(
            self.api_frame,
            text="Save API Settings",
            command=self.save_api_settings,
            fg_color=self.accent_color
        ).pack(pady=10)
        
        # Voice Settings
        self.voice_frame = ctk.CTkFrame(self.settings_scroll, fg_color='#222222')
        
        ctk.CTkLabel(
            self.voice_frame,
            text="Voice Settings",
            font=self.header_font
        ).pack(pady=10)
        
        # Speech rate
        ctk.CTkLabel(self.voice_frame, text="Speech Rate:").pack(anchor='w', padx=10)
        self.rate_var = tk.DoubleVar(value=config.get('voice.rate', 150))
        self.rate_slider = ctk.CTkSlider(
            self.voice_frame,
            from_=50,
            to=300,
            variable=self.rate_var,
            command=self.update_speech_rate
        )
        self.rate_slider.pack(pady=5, padx=10, fill='x')
        
        # Volume
        ctk.CTkLabel(self.voice_frame, text="Voice Volume:").pack(anchor='w', padx=10, pady=(10,0))
        self.volume_var = tk.DoubleVar(value=config.get('voice.volume', 0.8))
        self.volume_slider = ctk.CTkSlider(
            self.voice_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            command=self.update_voice_volume
        )
        self.volume_slider.pack(pady=5, padx=10, fill='x')
        
        # Language selection
        ctk.CTkLabel(self.voice_frame, text="Language:").pack(anchor='w', padx=10, pady=(10,0))
        self.language_var = tk.StringVar(value=config.get('languages.default', 'pt-BR'))
        self.language_menu = ctk.CTkOptionMenu(
            self.voice_frame,
            values=['pt-BR', 'en-US', 'es-ES', 'fr-FR', 'de-DE'],
            variable=self.language_var,
            command=self.update_language
        )
        self.language_menu.pack(pady=5, padx=10, fill='x')
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            height=30,
            fg_color='#111111'
        )
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=self.small_font,
            anchor='w'
        )
        
        # Time display
        self.time_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=self.small_font
        )
        
        self.update_time()
    
    def create_control_panel(self):
        """Create floating control panel"""
        self.control_panel = ctk.CTkFrame(
            self.main_frame,
            width=200,
            fg_color='#111111',
            corner_radius=15
        )
        
        # Quick action buttons
        ctk.CTkLabel(
            self.control_panel,
            text="Quick Actions",
            font=self.header_font
        ).pack(pady=10)
        
        # Emergency stop
        self.emergency_button = ctk.CTkButton(
            self.control_panel,
            text="🛑 Emergency Stop",
            command=self.emergency_stop,
            fg_color='#FF4444',
            hover_color='#CC3333',
            height=40
        )
        self.emergency_button.pack(pady=5, padx=10, fill='x')
        
        # Wake up JARVIS
        self.wake_button = ctk.CTkButton(
            self.control_panel,
            text="🎯 Wake JARVIS",
            command=self.wake_jarvis,
            fg_color=self.accent_color,
            height=40
        )
        self.wake_button.pack(pady=5, padx=10, fill='x')
        
        # System info
        self.quick_info_button = ctk.CTkButton(
            self.control_panel,
            text="📊 System Info",
            command=self.show_quick_info,
            fg_color='#666666',
            height=40
        )
        self.quick_info_button.pack(pady=5, padx=10, fill='x')
    
    def setup_layout(self):
        """Setup widget layout"""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header layout
        self.title_label.pack(side=tk.LEFT, padx=20, pady=20)
        self.subtitle_label.pack(side=tk.LEFT, padx=(0, 20))
        self.api_status_label.pack(side=tk.RIGHT, padx=20, pady=10)
        self.status_indicator.pack(side=tk.RIGHT, padx=(0, 10), pady=20)
        
        # Content area
        content_container = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Notebook
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Control panel
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        
        # Chat layout
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.send_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.voice_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.clear_button.pack(side=tk.RIGHT)
        
        # Camera layout
        self.camera_controls.pack(fill=tk.X, padx=10, pady=10)
        self.camera_toggle.pack(side=tk.LEFT, padx=5)
        self.photo_button.pack(side=tk.LEFT, padx=5)
        
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # System layout
        self.system_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.system_controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.volume_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Logs layout
        self.logs_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Settings layout
        self.settings_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.api_frame.pack(fill=tk.X, pady=10)
        self.voice_frame.pack(fill=tk.X, pady=10)
        
        # Status bar
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_text.pack(side=tk.LEFT, padx=10)
        self.time_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_jarvis_callbacks(self):
        """Setup JARVIS event callbacks"""
        self.jarvis_core.add_callback('on_wake_word', self.on_wake_word)
        self.jarvis_core.add_callback('on_command', self.on_command)
        self.jarvis_core.add_callback('on_response', self.on_response)
        self.jarvis_core.add_callback('on_error', self.on_error)
        self.jarvis_core.add_callback('on_status_change', self.on_status_change)
        
        # Test API connection
        if self.jarvis_core.ai_client:
            threading.Thread(
                target=self.test_api_connection,
                daemon=True
            ).start()
    
    def start_status_updates(self):
        """Start periodic status updates"""
        self.update_status()
        self.update_system_info()
        self.root.after(5000, self.start_status_updates)  # Update every 5 seconds
    
    # Event handlers
    def on_wake_word(self, data):
        """Handle wake word detection"""
        self.root.after(0, lambda: self.add_chat_message("System", "Wake word detected!", "#00FF00"))
        self.root.after(0, self.start_listening_animation)
    
    def on_command(self, data):
        """Handle voice command"""
        command_text = data.get('text', '')
        self.root.after(0, lambda: self.add_chat_message("You", command_text, self.accent_color))
    
    def on_response(self, data):
        """Handle JARVIS response"""
        response_text = data.get('text', '')
        self.root.after(0, lambda: self.add_chat_message("JARVIS", response_text, "#00FF00"))
    
    def on_error(self, error_msg):
        """Handle errors"""
        self.root.after(0, lambda: self.add_chat_message("Error", str(error_msg), "#FF4444"))
    
    def on_status_change(self, status):
        """Handle status changes"""
        status_map = {
            'idle': ('Ready', '#00FF00'),
            'listening': ('Listening...', '#FFAA00'),
            'processing': ('Processing...', '#00AAFF'),
            'speaking': ('Speaking...', '#AA00FF')
        }
        
        text, color = status_map.get(status, ('Unknown', '#FF4444'))
        self.root.after(0, lambda: self.update_status_indicator(text, color))
    
    # GUI Methods
    def add_chat_message(self, sender: str, message: str, color: str = None):
        """Add message to chat display"""
        if color is None:
            color = self.text_color
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state=tk.NORMAL)
        
        # Add timestamp and sender
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.chat_display.insert(tk.END, f"{sender}: ", 'sender')
        self.chat_display.insert(tk.END, f"{message}\n\n", 'message')
        
        # Configure tags
        self.chat_display.tag_configure('timestamp', foreground='#888888')
        self.chat_display.tag_configure('sender', foreground=color, font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure('message', foreground=color)
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send text message to JARVIS"""
        message = self.text_input.get().strip()
        if not message:
            return
        
        self.text_input.delete(0, tk.END)
        
        # Add to chat
        self.add_chat_message("You", message, self.accent_color)
        
        # Send to JARVIS
        threading.Thread(
            target=lambda: self.jarvis_core.command_queue.put({
                'text': message,
                'language': self.jarvis_core.current_language,
                'timestamp': datetime.now()
            }),
            daemon=True
        ).start()
    
    def start_voice_input(self):
        """Start voice input"""
        self.voice_button.configure(text="🎤 Listening...", state='disabled')
        self.add_chat_message("System", "Start speaking...", "#FFAA00")
        
        def listen():
            try:
                self.jarvis_core.start_listening()
            finally:
                self.root.after(0, lambda: self.voice_button.configure(
                    text="🎤 Listen", state='normal'
                ))
        
        threading.Thread(target=listen, daemon=True).start()
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state=tk.DISABLED)
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.jarvis_core.camera_manager.is_camera_active():
            self.jarvis_core.camera_manager.stop_camera()
            self.camera_toggle.configure(text="Start Camera", fg_color='#00AA00')
            self.photo_button.configure(state='disabled')
            self.camera_label.configure(text="Camera Feed\n(Click 'Start Camera' to begin)")
        else:
            if self.jarvis_core.camera_manager.start_camera():
                self.camera_toggle.configure(text="Stop Camera", fg_color='#FF4444')
                self.photo_button.configure(state='normal')
                self.start_camera_feed()
            else:
                messagebox.showerror("Error", "Failed to start camera")
    
    def start_camera_feed(self):
        """Start camera feed display"""
        def update_feed():
            if self.jarvis_core.camera_manager.is_camera_active():
                frame = self.jarvis_core.camera_manager.get_current_frame()
                if frame is not None:
                    # Convert to PhotoImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    image = image.resize((640, 480), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    self.camera_label.configure(image=photo, text="")
                    self.camera_label.image = photo  # Keep a reference
                
                self.root.after(100, update_feed)
        
        update_feed()
    
    def take_photo(self):
        """Take photo with camera"""
        try:
            filename = self.jarvis_core.camera_manager.take_photo()
            self.add_chat_message("System", f"Photo saved: {filename}", "#00FF00")
        except Exception as e:
            self.add_chat_message("Error", f"Failed to take photo: {e}", "#FF4444")
    
    def update_system_info(self):
        """Update system information display"""
        try:
            info = self.jarvis_core.system_controller.get_system_info()
            
            info_text = f"""
System Information:

Platform: {info.get('platform', 'Unknown')}
Processor: {info.get('processor', 'Unknown')}
CPU Count: {info.get('cpu_count', 'Unknown')}
CPU Usage: {info.get('cpu_percent', 0):.1f}%

Memory:
  Total: {info.get('memory_total', 0) / (1024**3):.1f} GB
  Used: {info.get('memory_used', 0) / (1024**3):.1f} GB
  Available: {info.get('memory_available', 0) / (1024**3):.1f} GB
  Usage: {info.get('memory_percent', 0):.1f}%

Disk:
  Total: {info.get('disk_total', 0) / (1024**3):.1f} GB
  Used: {info.get('disk_used', 0) / (1024**3):.1f} GB
  Free: {info.get('disk_free', 0) / (1024**3):.1f} GB
  Usage: {info.get('disk_percent', 0):.1f}%
"""
            
            self.system_info.configure(state=tk.NORMAL)
            self.system_info.delete(1.0, tk.END)
            self.system_info.insert(tk.END, info_text)
            self.system_info.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error updating system info: {e}")
    
    def add_log_entry(self, record):
        """Add log entry to logs display"""
        try:
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            level = record.levelname
            message = record.getMessage()
            
            log_text = f"[{timestamp}] {level}: {message}\n"
            
            self.root.after(0, lambda: self._add_log_text(log_text, level))
        except Exception as e:
            pass  # Ignore logging errors to prevent recursion
    
    def _add_log_text(self, text: str, level: str):
        """Add text to logs display"""
        try:
            self.logs_display.configure(state=tk.NORMAL)
            self.logs_display.insert(tk.END, text)
            
            # Color coding
            colors = {
                'DEBUG': '#888888',
                'INFO': '#FFFFFF',
                'WARNING': '#FFAA00',
                'ERROR': '#FF4444',
                'CRITICAL': '#FF0000'
            }
            
            color = colors.get(level, '#FFFFFF')
            start = self.logs_display.index("end-2l")
            end = self.logs_display.index("end-1l")
            
            self.logs_display.tag_add(level, start, end)
            self.logs_display.tag_configure(level, foreground=color)
            
            self.logs_display.configure(state=tk.DISABLED)
            self.logs_display.see(tk.END)
            
            # Keep only last 1000 lines
            lines = self.logs_display.get(1.0, tk.END).split('\n')
            if len(lines) > 1000:
                self.logs_display.configure(state=tk.NORMAL)
                self.logs_display.delete(1.0, f"{len(lines)-1000}.0")
                self.logs_display.configure(state=tk.DISABLED)
        except Exception:
            pass
    
    def update_status_indicator(self, text: str, color: str):
        """Update status indicator"""
        self.status_text.configure(text=text)
        self.status_indicator.configure(text_color=color)
    
    def update_status(self):
        """Update overall status"""
        status = self.jarvis_core.get_status()
        
        # Update API status
        if status.get('ai_available'):
            self.api_status_label.configure(
                text="API: Connected",
                text_color='#00FF00'
            )
        else:
            self.api_status_label.configure(
                text="API: Disconnected",
                text_color='#FF4444'
            )
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def start_listening_animation(self):
        """Start listening animation"""
        self.is_animating = True
        self.animate_title()
    
    def animate_title(self):
        """Animate title during listening"""
        if not self.is_animating:
            return
        
        colors = ['#00D4FF', '#0099CC', '#006699', '#003366']
        color = colors[self.animation_frame % len(colors)]
        
        self.title_label.configure(text_color=color)
        self.animation_frame += 1
        
        if self.jarvis_core.is_listening or self.jarvis_core.is_processing:
            self.root.after(200, self.animate_title)
        else:
            self.is_animating = False
            self.title_label.configure(text_color=self.accent_color)
    
    # Settings methods
    def save_api_settings(self):
        """Save API settings"""
        api_key = self.api_key_entry.get().strip()
        model = self.model_var.get().strip()
        
        if api_key:
            config.set('openrouter.api_key', api_key)
            config.set('openrouter.model', model)
            config.save_user_config()
            
            # Reinitialize AI client
            try:
                from ai.openrouter_client import OpenRouterClient
                self.jarvis_core.ai_client = OpenRouterClient()
                messagebox.showinfo("Success", "API settings saved successfully!")
                
                # Test connection
                threading.Thread(target=self.test_api_connection, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize API client: {e}")
        else:
            messagebox.showwarning("Warning", "Please enter an API key")
    
    def test_api_connection(self):
        """Test API connection"""
        if self.jarvis_core.ai_client:
            try:
                if self.jarvis_core.ai_client.test_connection():
                    self.root.after(0, lambda: self.update_status())
                    self.logger.info("API connection test successful")
                else:
                    self.logger.warning("API connection test failed")
            except Exception as e:
                self.logger.error(f"API connection test error: {e}")
    
    def update_speech_rate(self, value):
        """Update speech rate"""
        rate = int(float(value))
        self.jarvis_core.speech_engine.set_rate(rate)
        config.set('voice.rate', rate)
    
    def update_voice_volume(self, value):
        """Update voice volume"""
        volume = float(value)
        self.jarvis_core.speech_engine.set_volume(volume)
        config.set('voice.volume', volume)
    
    def update_language(self, language):
        """Update language setting"""
        self.jarvis_core.current_language = language
        self.jarvis_core.recognition_engine.set_language(language)
        config.set('languages.default', language)
    
    # Control methods
    def emergency_stop(self):
        """Emergency stop all operations"""
        try:
            self.jarvis_core.speech_engine.stop()
            self.jarvis_core.recognition_engine.stop()
            self.add_chat_message("System", "Emergency stop activated!", "#FF4444")
        except Exception as e:
            self.logger.error(f"Emergency stop error: {e}")
    
    def wake_jarvis(self):
        """Manually wake JARVIS"""
        self.jarvis_core.wake_word_detected = True
        self.jarvis_core.start_listening()
        self.add_chat_message("System", "JARVIS awakened manually", "#00FF00")
    
    def show_quick_info(self):
        """Show quick system info"""
        status = self.jarvis_core.get_status()
        info = f"""
JARVIS Status:

Listening: {status['is_listening']}
Speaking: {status['is_speaking']}
Processing: {status['is_processing']}
Language: {status['current_language']}
AI Available: {status['ai_available']}
Camera Active: {status['camera_active']}
Conversation Length: {status['conversation_length']}
"""
        messagebox.showinfo("JARVIS Status", info)
