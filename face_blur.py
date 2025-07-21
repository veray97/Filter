"""
Enhanced Selective Face Blur Application
A sophisticated real-time face blurring application that creates a transparent overlay window 
to selectively blur specific faces on your screen.
"""

import sys
import os
import cv2
import numpy as np
import face_recognition #this is the library that is used to detect and recognize faces
import mss
import gc
import time
from typing import Optional, List, Tuple
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QTimer, QRect, QPoint, 
                         QSize, QPropertyAnimation, QEasingCurve)
from PyQt6.QtGui import (QPainter, QPen, QPixmap, QImage, QFont, QColor, 
                        QCursor, QBrush, QPalette)


class FaceSelector: # this is for the window that pops up to select the face
    """Face selection dialog for choosing reference face"""
    
    def __init__(self):
        self.selected_encoding = None
        self.root = None
    
    def select_face(self) -> Optional[np.ndarray]:
        """Show face selection dialog and return face encoding"""
        self.root = tk.Tk()
        self.root.title("Select Reference Face")
        self.root.geometry("800x600")#this is the size of the window for the face selection dialog
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center') 
        
        # Main frame for the face selection dialog
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title for the face selection dialog
        title_label = ttk.Label(main_frame, text="Select Reference Face Image", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Choose a clear image with the face you want to blur.\n"
                                     "Requirements: Clear, well-lit, front-facing preferred.\n"
                                     "Supported formats: JPG, PNG, BMP, TIFF, WEBP", 
                                justify=tk.CENTER)
        instructions.pack(pady=(0, 20)) 
        
        # Image preview frame
        self.preview_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="10")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.image_label = ttk.Label(self.preview_frame, text="No image selected", 
                                    font=("Arial", 12), foreground="gray")
        self.image_label.pack(expand=True)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to select image", 
                                     font=("Arial", 10), foreground="blue")
        self.status_label.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))
        
        select_button = ttk.Button(button_frame, text="Select Image", 
                                  command=self._select_image, style="Accent.TButton")
        ok_button = ttk.Button(button_frame, text="Use This Face", 
                              command=self._on_ok, state=tk.DISABLED)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        
        select_button.pack(side=tk.LEFT, padx=(0, 10))#position of the select button
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        cancel_button.pack(side=tk.LEFT)
        
        self.ok_button = ok_button
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.mainloop()
        
        return self.selected_encoding #this is the face encoding that is selected
    
    def _select_image(self):
        """Handle image selection"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Reference Face Image",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        self._process_image(file_path)
    
    def _process_image(self, file_path: str):
        """Process selected image and extract face encoding"""
        try:
            self.status_label.config(text="Processing image...", foreground="orange")
            self.root.update()
            
            # Load and display image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Convert to RGB for face_recognition
            #rbg is for whole image, while face_locations is for each face
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #In the context of using the face_recognition library, converting an image to RGB format is an important step 
            #because the library expects images to be in RGB color space for accurate face detection and recognition.

            # Detect faces
            #the return value of face_locations is a list of tuples, each tuple contains the coordinates of a face in the image
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                self.status_label.config(text="ERROR: No face detected in image. Please choose another image.", 
                                       foreground="red")
                self.selected_encoding = None
                self.ok_button.config(state=tk.DISABLED)
                return
            
            # Get face encoding for first face
            #the return value of face_encodings is a list of face encodings, each encoding is a 128-dimensional vector that represents the face 
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if not face_encodings:
                self.status_label.config(text="ERROR: Could not encode face. Please choose another image.", 
                                       foreground="red")
                self.selected_encoding = None
                self.ok_button.config(state=tk.DISABLED) #if no face is detected, the ok button is disabled, so that the user cannot proceed
                return
            
            self.selected_encoding = face_encodings[0]
            
            # Display image with face detection
            self._display_image_with_faces(rgb_image, face_locations)
            
            # Update status #this can recognize multiple faces in the image
            face_count = len(face_locations)
            if face_count == 1:
                self.status_label.config(text="SUCCESS: One face detected and encoded.", 
                                       foreground="green")
            else:
                self.status_label.config(
                    text=f"WARNING: {face_count} faces detected. Using the first face for reference.", 
                    foreground="orange")
            
            self.ok_button.config(state=tk.NORMAL)#tk.normal is the state of the ok button, so that the user can proceed
            
        except Exception as e:
            self.status_label.config(text=f"ERROR: Error processing image: {str(e)}", 
                                   foreground="red")
            self.selected_encoding = None
            self.ok_button.config(state=tk.DISABLED)
    
    def _display_image_with_faces(self, rgb_image: np.ndarray, face_locations: List[Tuple]):
        """Display image with face detection rectangles"""
        # Create copy for drawing
        display_image = rgb_image.copy()
        
        # Draw rectangles around detected faces
        for i, (top, right, bottom, left) in enumerate(face_locations): #face_locations is a list of tuples, each tuple contains the coordinates of a face in the image
            color = (0, 255, 0) if i == 0 else (255, 255, 0)  # Green for first, yellow for others
            cv2.rectangle(display_image, (left, top), (right, bottom), color, 3)
            
            # Add label
            label = "Selected" if i == 0 else f"Face {i+1}"
            cv2.putText(display_image, label, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Resize for display
        height, width = display_image.shape[:2]
        max_size = 400 
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            display_image = cv2.resize(display_image, (new_width, new_height))
        
        # Convert to PIL and display 
        # PIL is a library that is used to create and manipulate images
        #ImageTk is a library that is used to display images in a tkinter window, and it is used to display the image in the face selection dialog
        pil_image = Image.fromarray(display_image) 
        photo = ImageTk.PhotoImage(pil_image) 
        
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo  # Keep a reference
    
    def _on_ok(self):
        self.root.destroy() #this is the function that is called when the user clicks the ok button
    
    def _on_cancel(self):
        self.selected_encoding = None
        self.root.destroy()


class BlurProcessor(QThread):
    """Thread for processing screen capture and face detection"""
    "(Only blur the part where face is detecedt. This logic is that, there will be latency, but the face not move like spaceship on screen. so even though you blur the face area that you detect maybe 0.01s ago, the face will still be there. This way, it will avoid the latency of whole screen playing)"
    frame_ready = pyqtSignal(object)  # Processed frame ready
    status_update = pyqtSignal(str)   # Status update
    error_occurred = pyqtSignal(str)      # Error message
    
    def __init__(self, reference_encoding: np.ndarray):
        super().__init__()
        self.reference_encoding = reference_encoding
        self.capture_area = None
        self.running = False
        
        # Face tracking for smooth, continuous blur
        self.last_face_pos = None  # Store last known face position
        self.face_history = []     # Keep history for smoothing
        self.max_history = 5       # Number of frames to average
        
        # Processing parameters - EXACT copy from reference
        self.detection_scale = 0.5  # Scale down for faster detection
        self.detection_model = "hog"  # Use HOG model for speed
        self.blur_strength = 31  # Must be odd number
        self.tolerance = 0.4  # Face matching tolerance
        
        # Initialize screen capture - EXACT copy from reference
        self.sct = mss.mss()
        self.frame_count = 0
        
        self.sct = mss.mss()
        
    def _smooth_face_position(self, face_locations):
        """Smooth face positions to prevent gaps and jitter"""
        if not face_locations:
            return face_locations
            
        # Take the first (most confident) face
        current_face = face_locations[0]
        
        # Add to history
        self.face_history.append(current_face)
        if len(self.face_history) > self.max_history:
            self.face_history.pop(0)
        
        # If we have enough history, smooth the position
        if len(self.face_history) >= 2:
            # Average the positions for smooth movement
            avg_top = sum(face[0] for face in self.face_history) // len(self.face_history)
            avg_right = sum(face[1] for face in self.face_history) // len(self.face_history)
            avg_bottom = sum(face[2] for face in self.face_history) // len(self.face_history)
            avg_left = sum(face[3] for face in self.face_history) // len(self.face_history)
            
            smoothed_face = (avg_top, avg_right, avg_bottom, avg_left)
            return [smoothed_face]
        
        return face_locations
        
    def _expand_face_area(self, face_location, expansion_factor=0.3):
        """Expand face area for better coverage and gap prevention"""
        top, right, bottom, left = face_location
        
        # Calculate expansion
        width = right - left
        height = bottom - top
        expand_w = int(width * expansion_factor)
        expand_h = int(height * expansion_factor)
        
        # Return expanded coordinates
        return (
            max(0, top - expand_h),
            right + expand_w,
            bottom + expand_h,
            max(0, left - expand_w)
        )
    
    def set_capture_area(self, x: int, y: int, width: int, height: int):
        """Set the area to capture and process - EXACT copy from reference"""
        self.capture_area = {
            "top": y,
            "left": x, 
            "width": width,
            "height": height
        }
    
    def stop(self):
        """Stop the processing thread"""
        self.running = False
        self.wait()  # Wait for thread to finish
        if hasattr(self, 'sct'):
            self.sct.close()
    
    def run(self):
        """Main processing loop"""
        self.running = True
        
        while self.running:
            try:
                if not hasattr(self, 'capture_area'):
                    time.sleep(0.001)
                    continue
                
                # Capture screen - EXACT copy from reference
                screenshot = self.sct.grab(self.capture_area)
                img_array = np.array(screenshot)
                
                # Convert BGRA to RGB - EXACT copy from reference
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
                
                # DEBUG: Show capture info every 30 frames
                # if self.frame_count % 30 == 0:
                #     print(f"DEBUG: Capture area: {self.capture_area}")
                #     print(f"DEBUG: Frame size: {img_rgb.shape}")
                
                # Process frame
                processed_frame = self._process_frame(img_rgb)
                
                if processed_frame is not None:
                    self.frame_ready.emit(processed_frame)
                    self.status_update.emit("Blurring Face")
                else:
                    # Emit None to indicate no face detected
                    self.frame_ready.emit(None)
                    self.status_update.emit("No Face Detected")
                
                # Control frame rate (30 FPS) - EXACT copy from reference
                time.sleep(1/60)
                
                # Periodic cleanup
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    gc.collect()
                
            except Exception as e:
                self.error_occurred.emit(f"Processing error: {str(e)}")
                time.sleep(0.0001)  # Prevent rapid error loops
    
    def _process_frame(self, img_rgb: np.ndarray) -> Optional[np.ndarray]:
        """Process a single frame to detect and blur matching faces - EXACT copy from reference
        
        Returns:
            np.ndarray: Processed frame with only blurred face areas visible
            None: When no matching face is found (for transparency)
        """
        try:
            # Use smaller image for faster face detection
            small_img = cv2.resize(img_rgb, (0, 0), fx=self.detection_scale, fy=self.detection_scale)
            face_locations = face_recognition.face_locations(small_img, model=self.detection_model, number_of_times_to_upsample=1)
            
            # print(f"DEBUG: Detected {len(face_locations)} faces in frame (scale={self.detection_scale})")
            
            if not face_locations:
                return None  # No faces detected - make window transparent
            
            # Scale face locations back to original size
            face_locations = [(int(top/self.detection_scale), int(right/self.detection_scale), 
                             int(bottom/self.detection_scale), int(left/self.detection_scale)) 
                            for (top, right, bottom, left) in face_locations]
            
            # Apply smoothing for continuous coverage
            face_locations = self._smooth_face_position(face_locations)
            
            # Get face encodings for detected faces
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            
            # print(f"DEBUG: Generated {len(face_encodings)} face encodings")
            
            # Create transparent overlay (RGBA format)
            overlay = np.zeros((img_rgb.shape[0], img_rgb.shape[1], 4), dtype=np.uint8)
            face_found = False
            
            # Check each face against target
            for i, ((top, right, bottom, left), face_encoding) in enumerate(zip(face_locations, face_encodings)):
                # Compare with target face
                matches = face_recognition.compare_faces([self.reference_encoding], 
                                                       face_encoding, tolerance=self.tolerance)
                
                # Calculate distance for debugging
                distances = face_recognition.face_distance([self.reference_encoding], face_encoding)
                
                # print(f"DEBUG: Face {i+1} - Match: {matches[0]}, Tolerance: {self.tolerance}, Distance: {distances[0]:.4f}")
                
                if matches[0]:  # Face matches target
                    face_found = True
                    
                    # Expand face area for gap-free coverage
                    expanded_face = self._expand_face_area((top, right, bottom, left), 0.2)
                    top, right, bottom, left = expanded_face
                    
                    # print(f"DEBUG: MATCH FOUND! Face coordinates: top={top}, right={right}, bottom={bottom}, left={left}")
                    # print(f"DEBUG: Face size: width={right-left}, height={bottom-top}")
                    # print(f"DEBUG: Image size: width={img_rgb.shape[1]}, height={img_rgb.shape[0]}")
                    
                    # Ensure coordinates are within bounds
                    top = max(0, top)
                    left = max(0, left)
                    bottom = min(img_rgb.shape[0], bottom)
                    right = min(img_rgb.shape[1], right)
                    
                    # print(f"DEBUG: Bounded coordinates: top={top}, right={right}, bottom={bottom}, left={left}")
                    # print(f"DEBUG: Bounded face size: width={right-left}, height={bottom-top}")
                    
                    # Extract and blur face region with padding for continuity
                    face_region = img_rgb[top:bottom, left:right]
                    if face_region.size > 0:
                        blurred_face = cv2.GaussianBlur(face_region, 
                                                      (self.blur_strength, self.blur_strength), 0)
                        
                        # Expand blur area for continuous coverage
                        face_height = bottom - top
                        face_width = right - left
                        
                        # Add padding for gap-free coverage (20% larger)
                        padding_h = int(face_height * 0.1)
                        padding_w = int(face_width * 0.1)
                        
                        # Expand coordinates with padding
                        padded_top = max(0, top - padding_h)
                        padded_left = max(0, left - padding_w)
                        padded_bottom = min(img_rgb.shape[0], bottom + padding_h)
                        padded_right = min(img_rgb.shape[1], right + padding_w)
                        
                        # Extract larger region for blur
                        padded_region = img_rgb[padded_top:padded_bottom, padded_left:padded_right]
                        blurred_padded = cv2.GaussianBlur(padded_region, 
                                                        (self.blur_strength, self.blur_strength), 0)
                        
                        # Create circular mask for smooth, continuous coverage
                        padded_height = padded_bottom - padded_top
                        padded_width = padded_right - padded_left
                        
                        # Use circular mask that's 110% of face size for overlap
                        mask = np.zeros((padded_height, padded_width), dtype=np.uint8)
                        center_x, center_y = padded_width // 2, padded_height // 2
                        radius = max(face_width, face_height) // 2 + 20  # Extra radius for continuity
                        
                        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
                        
                        # Apply strong gaussian blur for seamless edges
                        mask = cv2.GaussianBlur(mask, (41, 41), 0)  # Larger blur for smoother transitions
                        
                        # Apply the blurred region with smooth mask
                        for c in range(3):  # RGB channels
                            overlay[padded_top:padded_bottom, padded_left:padded_right, c] = blurred_padded[:, :, c]
                        
                        # Use the smooth mask as alpha channel
                        overlay[padded_top:padded_bottom, padded_left:padded_right, 3] = mask
            
            if not face_found:
                return None  # No matching faces - make window transparent
            
            # Return only the RGBA overlay (with transparency)
            # The paintEvent will handle displaying only the non-transparent parts
            return overlay
                            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return None


class EnhancedBlurWindow(QMainWindow):
    """Main overlay window with enhanced controls"""
    
    def __init__(self, reference_encoding: np.ndarray):
        super().__init__()
        self.reference_encoding = reference_encoding
        self.processor = None
        self.current_pixmap = None  # Store current blurred content
        
        # Window properties
        self.border_width = 8
        self.min_size = QSize(300, 200)
        self.resize_margin = 10
        
        # State tracking
        self.dragging = False
        self.resizing = False
        self.resize_direction = ""
        self.last_mouse_pos = QPoint()
        
        self.setup_ui()
        self.setup_processor()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
        # Note: Removed aggressive keep-on-top timer to prevent keyboard focus issues
    
    def setup_ui(self):
        """Setup the user interface"""
        # Window configuration - EXACT copy from reference for always on top
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Window | 
                           Qt.WindowType.FramelessWindowHint)
        
        # Transparency attributes - EXACT copy from reference  
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # CRITICAL: Allow keyboard input to pass through to other applications
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Set initial size and position
        self.setGeometry(100, 100, 600, 400)
        
        # No central widget - we'll draw directly on the window
        self.central_widget = None
        
        # Status label positioned at top
        self.status_label = QLabel(self)
        self.status_label.setGeometry(10, 10, 200, 30)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 5px 10px;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 100);
            }
        """)
        self.status_label.setText("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def setup_processor(self):
        """Setup the blur processor thread"""
        self.processor = BlurProcessor(self.reference_encoding)
        self.processor.frame_ready.connect(self.update_frame)
        self.processor.status_update.connect(self.update_status_text)
        self.processor.error_occurred.connect(self.handle_error)
        
        # Set capture area and start processing
        self.update_processor_capture_rect()
        self.processor.start()
    
    def paintEvent(self, event):
        """Paint the blurred face overlay with red border for visibility"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background with fully transparent
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        # Draw the blurred content if available
        if self.current_pixmap:
            painter.drawPixmap(0, 0, self.current_pixmap)
        
        # Draw red border around the entire window for visibility
        pen = QPen(QColor(255, 0, 0), 3)  # Red border, 3px thick
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        rect = self.rect().adjusted(1, 1, -2, -2)  # Adjust for border width
        painter.drawRect(rect)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.globalPosition().toPoint()
            
            # Check if clicking on resize area
            resize_dir = self.get_resize_direction(event.position().toPoint())
            if resize_dir:
                self.resizing = True
                self.resize_direction = resize_dir
                self.setCursor(self.get_resize_cursor(resize_dir))
            else:
                # Check if in draggable area (center)
                if self.is_in_drag_area(event.position().toPoint()):
                    self.dragging = True
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        current_pos = event.globalPosition().toPoint()
        
        if self.resizing:
            self.handle_resize(current_pos)
        elif self.dragging:
            self.handle_drag(current_pos)
        else:
            # Update cursor based on position
            self.update_cursor(event.position().toPoint())
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_direction = ""
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def get_resize_direction(self, pos: QPoint) -> str:
        """Determine resize direction based on mouse position"""
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        margin = self.resize_margin
        
        # Corner resize
        if x <= margin and y <= margin:
            return "top-left"
        elif x >= w - margin and y <= margin:
            return "top-right"
        elif x <= margin and y >= h - margin:
            return "bottom-left"
        elif x >= w - margin and y >= h - margin:
            return "bottom-right"
        
        # Edge resize
        elif x <= margin:
            return "left"
        elif x >= w - margin:
            return "right"
        elif y <= margin:
            return "top"
        elif y >= h - margin:
            return "bottom"
        
        return ""
    
    def get_resize_cursor(self, direction: str) -> Qt.CursorShape:
        """Get appropriate cursor for resize direction"""
        cursor_map = {
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top-left": Qt.CursorShape.SizeFDiagCursor,
            "bottom-right": Qt.CursorShape.SizeFDiagCursor,
            "top-right": Qt.CursorShape.SizeBDiagCursor,
            "bottom-left": Qt.CursorShape.SizeBDiagCursor,
        }
        return cursor_map.get(direction, Qt.CursorShape.ArrowCursor)
    
    def is_in_drag_area(self, pos: QPoint) -> bool:
        """Check if position is in draggable area"""
        margin = self.resize_margin
        # Exclude status label area from dragging
        status_area = QRect(5, 5, 210, 40)
        if status_area.contains(pos):
            return False
        return (margin < pos.x() < self.width() - margin and 
                margin < pos.y() < self.height() - margin)
    
    def update_cursor(self, pos: QPoint):
        """Update cursor based on mouse position"""
        resize_dir = self.get_resize_direction(pos)
        if resize_dir:
            self.setCursor(self.get_resize_cursor(resize_dir))
        elif self.is_in_drag_area(pos):
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def handle_resize(self, current_pos: QPoint):
        """Handle window resizing"""
        delta = current_pos - self.last_mouse_pos
        self.last_mouse_pos = current_pos
        
        geometry = self.geometry()
        
        if "left" in self.resize_direction:
            geometry.setLeft(geometry.left() + delta.x())
        if "right" in self.resize_direction:
            geometry.setRight(geometry.right() + delta.x())
        if "top" in self.resize_direction:
            geometry.setTop(geometry.top() + delta.y())
        if "bottom" in self.resize_direction:
            geometry.setBottom(geometry.bottom() + delta.y())
        
        # Enforce minimum size
        if geometry.width() < self.min_size.width():
            if "left" in self.resize_direction:
                geometry.setLeft(geometry.right() - self.min_size.width())
            else:
                geometry.setRight(geometry.left() + self.min_size.width())
        
        if geometry.height() < self.min_size.height():
            if "top" in self.resize_direction:
                geometry.setTop(geometry.bottom() - self.min_size.height())
            else:
                geometry.setBottom(geometry.top() + self.min_size.height())
        
        self.setGeometry(geometry)
        # CRITICAL: Update capture area immediately for responsive resizing
        self.update_processor_capture_rect()
        self.update()  # Force repaint immediately
    
    def handle_drag(self, current_pos: QPoint):
        """Handle window dragging"""
        delta = current_pos - self.last_mouse_pos
        self.last_mouse_pos = current_pos
        self.move(self.pos() + delta)
        # CRITICAL: Update capture area immediately when moving
        self.update_processor_capture_rect()
        self.update()  # Force repaint immediately
    
    def update_processor_capture_rect(self):
        """Update processor's capture rectangle"""
        if self.processor:
            # Capture entire window area (no border offset)
            self.processor.set_capture_area(self.x(), self.y(), self.width(), self.height())
    
    def update_frame(self, processed_frame):
        """Update window with new processed frame"""
        if processed_frame is not None:
            # Check if the frame has the correct dimensions
            if len(processed_frame.shape) != 3:
                print(f"DEBUG: Invalid frame shape: {processed_frame.shape}, size: {processed_frame.size}, type: {type(processed_frame)}")
                self.current_pixmap = None
                self.update()
                return
                
            # Convert RGBA numpy array to QImage with transparency
            height, width, channels = processed_frame.shape
            
            # Ensure we have 4 channels (RGBA)
            if channels != 4:
                print(f"Invalid channel count: {channels}, expected 4 (RGBA)")
                self.current_pixmap = None
                self.update()
                return
                
            bytes_per_line = channels * width
            
            # Ensure the array is contiguous
            processed_frame_contiguous = np.ascontiguousarray(processed_frame)
            
            # Create QImage from RGBA data
            q_image = QImage(processed_frame_contiguous.data.tobytes(),
                           width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
            
            # Convert to QPixmap and scale to window size
            self.current_pixmap = QPixmap.fromImage(q_image).scaled(
                self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Make window visible
            if not self.isVisible():
                self.show()
        else:
            # No face detected - make transparent
            self.current_pixmap = None
        
        # Trigger repaint
        self.update()
    
    def update_status_text(self, status: str):
        """Update status text"""
        size_text = f" • {self.width()}×{self.height()}"
        self.status_label.setText(f"{status}{size_text}")
    
    def update_status(self):
        """Periodic status update"""
        if hasattr(self, 'processor') and self.processor:
            # This will be updated by processor signals
            pass
        else:
            self.status_label.setText("Initializing...")
    

    
    def resizeEvent(self, event):
        """Handle window resize to update status label position"""
        super().resizeEvent(event)
        if hasattr(self, 'status_label'):
            # Keep status label in top-left corner
            self.status_label.setGeometry(10, 10, 200, 30)
        
        # CRITICAL: Update capture area immediately on any resize
        if hasattr(self, 'processor') and self.processor:
            self.update_processor_capture_rect()
            self.update()  # Force immediate repaint
    
    def handle_error(self, error_msg: str):
        """Handle processor errors"""
        print(f"Processor error: {error_msg}")
        self.status_label.setText(f"Error: {error_msg}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.processor:
            self.processor.stop()
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        event.accept()


class FaceBlurApplication:
    """Main application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def run(self):
        """Run the complete application flow"""
        # Start directly with face selection
        face_selector = FaceSelector()
        reference_encoding = face_selector.select_face()
        
        if reference_encoding is None:
            messagebox.showinfo("Cancelled", "Face selection cancelled. Application will exit.")
            return
        
        # Create PyQt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(True)
        
        # Create and show main window
        self.main_window = EnhancedBlurWindow(reference_encoding)
        self.main_window.show()
        
        # Handle application shutdown
        def cleanup():
            if self.main_window:
                self.main_window.close()
        
        self.app.aboutToQuit.connect(cleanup)
        
        # Run application
        try:
            sys.exit(self.app.exec())
        except KeyboardInterrupt:
            cleanup()
            sys.exit(0)


def main():
    """Main entry point"""
    try:
        app = FaceBlurApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
