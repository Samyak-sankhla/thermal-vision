# Thermal Camera Intrinsic Calibration

Calibrate thermal camera intrinsic parameters using a checkerboard pattern.

## Overview

This module estimates the intrinsic camera matrix and lens distortion coefficients of a thermal camera. Unlike RGB cameras, thermal cameras present unique challenges due to low contrast and indistinct edges, making standard calibration unreliable.

## The Problem & Solution

### Why Thermal Cameras Are Different

Thermal cameras capture infrared radiation, not visible light. This creates several issues for standard calibration:
- Printed checkerboard patterns appear uniform (same temperature as background)
- Edges are not clearly distinguishable
- Corner detection fails without temperature contrast

### Thermally Enhanced Checkerboard Solution

The approach uses a physically modified checkerboard:
- Print a standard checkerboard on white paper
- Cover alternate black squares with aluminum foil
- Aluminum foil has different thermal emissivity than paper
- When exposed to ambient conditions or gentle heating, foil and paper reach different temperatures
- This creates a clear temperature gradient visible in thermal images
- Checkerboard corners become reliably detectable

## Workflow Steps

### Step 1: Generate Checkerboard Pattern

**File:** `a4_checkerboard.py`

**What it does:**
- Generates an A4-sized (210mm × 297mm) checkerboard pattern
- Pattern is optimized for 300 DPI printing
- Centers the pattern on the A4 page

**Output:** `checkerboard.png`

**Run:**
```bash
python src/a4_checkerboard.py
```

**Next steps:**
1. Print `checkerboard.png` on A4 white paper (use 1:1 scale, no automatic scaling)
2. Cover all BLACK squares with aluminum foil (any side facing outward works)
3. Mount on rigid, flat surface (wood board, foam board, or plastic sheet)
4. Heat the board using a hair dryer or blower right before capturing frames. This creates a temperature gradient between the foil and paper, making corners more visible to the thermal camera.

---

### Step 2: Setup Camera and Capture Frames

**File:** `camera_setup.py`

**What it does:**
- Automatically scans camera ports (0-7) to find thermal camera
- Auto-creates `data/` folder for storing frames
- Displays live thermal camera video stream with minimal UI
- Normalizes thermal data to visible contrast range
- Allows saving individual frames on demand
- Shows frame counter and keyboard controls on screen

**How to use:**
```bash
python src/camera_setup.py
```

**Execution flow:**
1. Scans ports 0-4 to find connected thermal camera
2. On success: Prints `Camera found at port: X`
3. Opens video window titled "Thermal Camera"
4. Starts continuous capture loop
5. Each frame is normalized and displayed
6. Shows UI with save counter and keyboard instructions

**Controls:**
- Press **'s'** - Save current frame (saved as `data/frame_00.png`, `data/frame_01.png`, etc.)
- Press **'q'** - Exit program gracefully

**Capture Strategy:**
- Position camera perpendicular to checkerboard
- Move to 3-4 different angles (left, right, tilted)
- Vary distances: close (30cm), medium (60cm), far (100cm)
- Ensure checkerboard fills 40-80% of image frame
- Save 10-20 frames total (more = better calibration)
- Vary viewing angle by 20-30 degrees between frames

**Saved Output:**
- Frames saved to `data/` directory
- File naming: `frame_00.png`, `frame_01.png`, etc. (zero-padded)
- Format: Normalized grayscale thermal data
- Size: Original camera resolution

---

### Step 3: Perform Calibration

**File:** `calibrate.py`

**What it does:**
- Loads all frames from `data/` folder
- Applies preprocessing to enhance thermal contrast
- Detects checkerboard corner positions in each frame
- Refines positions to sub-pixel accuracy
- Displays detected corners as wireframe overlays
- Requests user validation (accept/reject) for each image
- Performs intrinsic calibration using OpenCV
- Calculates calibration quality metric (reprojection error)
- Saves calibration parameters to file
- **Saves accepted images with wireframes to `output/` folder**

**Configuration (edit in the script):**
```python
CHECKERBOARD = (9, 6)   # Inner corners: (columns, rows)
SQUARE_SIZE = 20        # Square size in millimeters
```
**Important:** SQUARE_SIZE must match physical checkerboard dimensions.

**Run:**
```bash
python src/calibrate.py
```

---

## Calibration Quality Interpretation

Judge calibration using reprojection error:

| Error Range | Quality | Action |
|-------------|---------|--------|
| < 0.5 px | Excellent | Accept and use |
| 0.5 - 1.0 px | Good | Use with confidence |
| 1.0 - 2.0 px | Acceptable | Use, but could improve |
| > 2.0 px | Poor | Recalibrate |

## Understanding Output Parameters

### Camera Intrinsic Matrix (K)
3×3 matrix encoding fundamental camera properties:
- **fx, fy** (diagonal): Focal length in pixels (magnification factor)
- **cx, cy** (top-right): Principal point = optical axis intersection on sensor
- Typically remain constant for fixed lens
- Different for different focal lengths or lens configurations

### Distortion Coefficients
Polynomial model of lens imperfections:
- **k1, k2, k3**: Radial distortion (barrel/pincushion curvature)
- **p1, p2**: Tangential distortion (decentering)
- Enable undistortion of images: `cv2.undistort(image, K, dist)`

---

## File Structure

```
intrinsic/
├── src/
│   ├── a4_checkerboard.py    # Generate checkerboard pattern
│   ├── camera_setup.py       # Capture thermal frames
│   └── calibrate.py          # Perform calibration
├── data/
│   └── frame_00.png, frame_01.png, ...  (saved by camera_setup.py)
├── output/
│   └── accepted_00.png, accepted_01.png, ...  (saved by calibrate.py with wireframes)
├── requirements.txt
└── README.md
```

## Dependencies

**Install:**
```bash
pip install -r requirements.txt
```

## Troubleshooting

**Camera not found:**
- Verify thermal camera is connected and powered
- Try different USB ports
- Check device manager for camera driver
- Edit `camera_setup.py` to manually specify port if known

**No checkerboard corners detected:**
- Ensure aluminum foil covers all black squares
- Verify checkerboard is flat (not bent/wrinkled)
- Check thermal contrast exists (touch foil/paper - should feel different)
- Improve lighting or heating for better contrast
- Try closer distance to board

**High reprojection error (> 2.0 pixels):**
- Capture more frames (target 15-20)
- Use wider range of angles and distances
- Ensure checkerboard remains flat and rigid
- Verify SQUARE_SIZE matches physical dimensions
- Recalibrate with enhanced thermal contrast setup

**Calibration fails (< 5 valid images):**
- Accept more images during validation (lower standards)
- Recapture with better image quality
- Verify checkerboard is visible in thermal images
- Check camera is outputting thermal data

