"""
Camera Manager Module
Handles camera operations and computer vision
"""

import cv2
import threading
import time
from datetime import datetime
import os
from typing import Optional, Callable, Tuple
import numpy as np

from config.config import config
from utils.logger import get_logger

class CameraManager:
    """Camera management and computer vision operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Configuration
        self.device_id = config.get('camera.device_id', 0)
        self.width = config.get('camera.width', 640)
        self.height = config.get('camera.height', 480)
        self.fps = config.get('camera.fps', 30)
        
        # Camera object
        self.camera = None
        self.is_active = False
        self.is_recording = False
        
        # Threading
        self.capture_thread = None
        self.frame_lock = threading.Lock()
        self.current_frame = None
        
        # Callbacks
        self.frame_callbacks = []
        self.detection_callbacks = []
        
        # Face detection (optional)
        self.face_cascade = None
        self._load_face_detection()
        
        # Create output directory
        os.makedirs('output/photos', exist_ok=True)
        os.makedirs('output/videos', exist_ok=True)
    
    def _load_face_detection(self):
        """Load face detection classifier"""
        try:
            # Try to load OpenCV's face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                self.logger.info("Face detection loaded")
            else:
                self.logger.warning("Face detection cascade not found")
                
        except Exception as e:
            self.logger.warning(f"Could not load face detection: {e}")
    
    def start_camera(self) -> bool:
        """Start camera capture"""
        if self.is_active:
            self.logger.warning("Camera is already active")
            return True
        
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(self.device_id)
            
            if not self.camera.isOpened():
                self.logger.error("Could not open camera")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Start capture thread
            self.is_active = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            self.capture_thread.start()
            
            self.logger.info("Camera started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture"""
        if not self.is_active:
            return
        
        try:
            self.is_active = False
            self.is_recording = False
            
            # Wait for capture thread to finish
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2)
            
            # Release camera
            if self.camera:
                self.camera.release()
                self.camera = None
            
            with self.frame_lock:
                self.current_frame = None
            
            self.logger.info("Camera stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping camera: {e}")
    
    def _capture_loop(self):
        """Main camera capture loop"""
        while self.is_active and self.camera:
            try:
                ret, frame = self.camera.read()
                
                if not ret:
                    self.logger.warning("Failed to read frame")
                    continue
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Update current frame
                with self.frame_lock:
                    self.current_frame = processed_frame.copy()
                
                # Trigger callbacks
                for callback in self.frame_callbacks:
                    try:
                        callback(processed_frame)
                    except Exception as e:
                        self.logger.debug(f"Frame callback error: {e}")
                
                # Small delay to prevent CPU overload
                time.sleep(1 / self.fps)
                
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                break
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process camera frame"""
        try:
            # Face detection
            if self.face_cascade is not None and config.get('features.face_recognition', False):
                faces = self._detect_faces(frame)
                
                # Draw face rectangles
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        frame, "Face", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
                    )
                
                # Trigger detection callbacks
                if len(faces) > 0:
                    for callback in self.detection_callbacks:
                        try:
                            callback('face', faces)
                        except Exception as e:
                            self.logger.debug(f"Detection callback error: {e}")
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                frame, timestamp, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
            )
            
            # Add JARVIS overlay
            cv2.putText(
                frame, "JARVIS - ACTIVE", (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1
            )
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return frame
    
    def _detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            return faces
            
        except Exception as e:
            self.logger.debug(f"Face detection error: {e}")
            return []
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get current camera frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def take_photo(self, filename: Optional[str] = None) -> str:
        """Take a photo"""
        if not self.is_active:
            raise RuntimeError("Camera is not active")
        
        frame = self.get_current_frame()
        if frame is None:
            raise RuntimeError("No frame available")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/photos/jarvis_photo_{timestamp}.jpg"
        
        try:
            cv2.imwrite(filename, frame)
            self.logger.info(f"Photo saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving photo: {e}")
            raise
    
    def start_recording(self, filename: Optional[str] = None) -> str:
        """Start video recording"""
        if not self.is_active:
            raise RuntimeError("Camera is not active")
        
        if self.is_recording:
            raise RuntimeError("Already recording")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/videos/jarvis_video_{timestamp}.mp4"
        
        try:
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                filename, fourcc, self.fps, (self.width, self.height)
            )
            
            self.is_recording = True
            self.recording_filename = filename
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._recording_loop,
                daemon=True
            )
            self.recording_thread.start()
            
            self.logger.info(f"Recording started: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            raise
    
    def stop_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        try:
            self.is_recording = False
            
            # Wait for recording thread
            if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2)
            
            # Release video writer
            if hasattr(self, 'video_writer'):
                self.video_writer.release()
            
            self.logger.info(f"Recording stopped: {getattr(self, 'recording_filename', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
    
    def _recording_loop(self):
        """Video recording loop"""
        while self.is_recording:
            try:
                frame = self.get_current_frame()
                if frame is not None and hasattr(self, 'video_writer'):
                    self.video_writer.write(frame)
                
                time.sleep(1 / self.fps)
                
            except Exception as e:
                self.logger.error(f"Error in recording loop: {e}")
                break
    
    def add_frame_callback(self, callback: Callable):
        """Add frame processing callback"""
        self.frame_callbacks.append(callback)
    
    def add_detection_callback(self, callback: Callable):
        """Add detection callback"""
        self.detection_callbacks.append(callback)
    
    def is_camera_active(self) -> bool:
        """Check if camera is active"""
        return self.is_active
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        return {
            'device_id': self.device_id,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'is_active': self.is_active,
            'is_recording': self.is_recording,
            'face_detection_available': self.face_cascade is not None
        }
