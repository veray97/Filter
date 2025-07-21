# Filter
This is a pop-up window with filtering function to blur the face you don't want to see on your screen


A sophisticated real-time face blurring application that creates a transparent overlay window to selectively blur specific faces on your screen.

## 🌟 Features

### Core Functionality
- **Selective Face Recognition**: Choose a reference face from an image
- **Real-Time Processing**: 60 FPS screen capture and face detection
- **Transparent Overlay**: Always-on-top of screen
- **Selective Blurring**: Only blurs faces matching your reference. 

### User Interface
- **Resizable Window**: Drag borders and corners to resize
- **Draggable**: Move window by dragging the center area
- **Visual Indicators**: Clear border and corner resize cues
- **Status Display**: Real-time status and size information

### Technical Features
- **Memory Optimized**: Efficient memory management with garbage collection
- **Error Handling**: Comprehensive error handling and user feedback
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **High Performance**: Optimized face detection and image processing

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- 4GB+ RAM recommended
- Modern CPU (Intel i5/AMD Ryzen 5 or better)
- Graphics support for OpenCV

### Dependencies
All dependencies are listed in `requirements_enhanced.txt`:

```bash
# Install dependencies
pip install -r requirements_enhanced.txt
```

### Core Libraries
- **PyQt6**: GUI framework for the overlay window
- **OpenCV**: Image processing and blurring effects
- **face_recognition**: Face detection and recognition
- **mss**: High-speed screen capture
- **NumPy**: Numerical operations
- **Pillow**: Image handling

## 🚀 Installation

### 1. Clone or Download
```bash
# If using git
git clone <repository-url>
cd ICWIS

# Or download the files directly
```

### 2. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or using conda
conda install --file requirements.txt
```

### 3. Download Face Recognition Models
The `dlib` library requires face landmark models. If you encounter issues, you may need to download them manually:

```bash
# The shape_predictor_68_face_landmarks.dat file should be in the same directory
# It's already included in this repository
```

## 📖 Usage

### Starting the Application
```bash
python face_blur.py
```

### Step-by-Step Process


#### 1. Face Selection
- **Select Image**: Click "📁 Select Image" to choose a reference photo
- **Image Requirements**:
  - Clear, well-lit face
  - Front-facing preferred
  - Supported formats: JPG, PNG, BMP, TIFF, WEBP
- **Processing**: The app will detect faces in your image
- **Results**:
  - ✅ One face: Perfect! Face encoding saved
  - ⚠️ Multiple faces: First face selected automatically
  - ❌ No faces: Choose a different image

#### 2. Blur Window
- A red-bordered overlay window appears
- **Controls**:
  - **Resize**: Drag red borders or corners
  - **Move**: Drag the center area
  - **Close**: Click the X or press Ctrl+C in terminal

#### 3. Real-Time Blurring
- Position the window over content you want to monitor
- Matching faces are automatically blurred in real-time
- Non-matching faces remain unblurred
- Window updates at 30 FPS for smooth performance

## 🎛️ Controls and Interactions

### Window Controls
| Action | Method |
|--------|--------|
| **Resize** | Drag red border edges or corners |
| **Move** | Drag center area of window |
| **Close** | Close window or Ctrl+C in terminal |

### Mouse Cursors
- **↔️ ↕️**: Resize horizontally/vertically
- **↗️ ↙️**: Resize diagonally
- **✋**: Move window
- **→**: Normal cursor

### Status Bar
- **Active/Inactive**: Processing status
- **Size**: Current window dimensions
- **Instructions**: Quick help text

## ⚙️ Configuration

### Adjustable Parameters
You can modify these parameters in the code:

```python
# In BlurProcessor class
self.blur_strength = 51        # Blur intensity (higher = more blur)
self.detection_scale = 0.5     # Detection speed vs accuracy
self.tolerance = 0.6           # Face matching sensitivity

# In EnhancedBlurWindow class
self.border_width = 8          # Border thickness
self.min_size = (300, 200)     # Minimum window size
```

### Performance Tuning
- **High Performance**: Lower `detection_scale` (0.3-0.4)
- **High Accuracy**: Higher `detection_scale` (0.6-0.8)
- **More Blur**: Increase `blur_strength` (71, 99, 127)
- **Less Blur**: Decrease `blur_strength` (31, 21, 15)

## 🔧 Troubleshooting

### Common Issues

#### "No face detected in image"
- **Solution**: Use a clearer, well-lit image
- **Tips**: Front-facing photos work best
- **Check**: Image isn't too dark or blurry

#### "Application won't start"
- **Check**: Python version (3.7+)
- **Verify**: All dependencies installed correctly
- **Try**: Reinstalling requirements

#### "Window not responding"
- **Cause**: Heavy system load
- **Solution**: Close other applications
- **Check**: Available RAM and CPU usage

#### "Face not being blurred"
- **Adjust**: Face matching tolerance in code
- **Try**: Different reference image
- **Check**: Target face is clearly visible

### Performance Issues
- **Slow detection**: Lower `detection_scale`
- **High CPU usage**: Increase timer intervals
- **Memory issues**: Restart application periodically

### Error Messages
- **"Processing error"**: Usually temporary, window will recover
- **"Capture failed"**: Check screen permissions
- **"Face encoding failed"**: Try different reference image

## 🔒 Privacy and Security

### Data Handling
- **Local Processing**: All face recognition happens locally
- **No Network**: No data sent to external servers
- **Temporary Storage**: Face encodings only stored in memory
- **No Logging**: No personal data is logged or saved

### Permissions
- **Screen Capture**: Required for overlay functionality
- **File Access**: Only for loading reference images
- **No Camera**: Does not access webcam or other cameras

## 🎯 Use Cases

### Professional
- **Privacy Protection**: Blur faces in screen recordings
- **Presentations**: Hide sensitive identity information
- **Live Streaming**: Real-time face anonymization
- **Content Creation**: Protect privacy in tutorials

### Personal
- **Screen Sharing**: Protect identity during video calls
- **Social Media**: Blur faces before posting screenshots
- **Family Privacy**: Protect children's faces in content
- **Security**: Hide identity in sensitive communications

## 🔄 Technical Details

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Face Selector │    │  Main Window     │    │ Blur Processor  │
│   (Tkinter)     │───▶│  (PyQt6)         │◄──▶│ (QThread)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Screen Display  │    │ Face Recognition│
                       │  (OpenGL/Qt)     │    │ (dlib/OpenCV)   │
                       └──────────────────┘    └─────────────────┘
```

### Threading Model
- **Main Thread**: UI updates and user interactions
- **Processor Thread**: Screen capture and face detection
- **Timer Events**: Status updates and periodic cleanup

### Memory Management
- Automatic garbage collection every 30 frames
- Image buffer reuse to minimize allocations
- Cleanup on window close and application exit

## 🤝 Contributing

### Reporting Issues
- Describe the problem clearly
- Include system information (OS, Python version)
- Provide error messages if any
- Include steps to reproduce

### Feature Requests
- Explain the use case
- Describe the desired functionality
- Consider performance implications

## 📄 License

This project is provided as-is for educational and personal use. Please respect privacy laws and obtain consent before using face recognition technology on others.

## 🆘 Support

For issues and questions:
1. Check this README first
2. Review error messages in terminal
3. Try the troubleshooting section
4. Search for similar issues online
