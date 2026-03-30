import cv2
import numpy as np
import glob
import os

# Configuration
CHECKERBOARD = (9, 6)  # (cols, rows) - inner corners
SQUARE_SIZE = 20  # mm

# Create output folder
if not os.path.exists("output"):
    os.makedirs("output")

# Load images from data folder
images = sorted(glob.glob("data/frame_*.png"))
print(f"Found {len(images)} images")

if not images:
    print("No images found in data/ folder")
    exit()

# Prepare object points (3D world coordinates)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D points in world coordinates
imgpoints = []  # 2D points in image plane
accepted_count = 0  # Counter for accepted images

# Process each image
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Preprocessing for thermal images
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.equalizeHist(gray)
    
    # Detect checkerboard corners
    ret, corners = cv2.findChessboardCorners(
        gray, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    
    display = img.copy()
    
    if ret:
        # Refine corner positions
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        # Draw the checkerboard wireframe
        cv2.drawChessboardCorners(display, CHECKERBOARD, corners, ret)
        print(f"Processing: {fname} - Corners detected")
    else:
        print(f"Processing: {fname} - No corners found")
    
    # Show image with detected corners
    cv2.imshow("Press y=accept, n=reject, ESC=skip all", display)
    key = cv2.waitKey(0) & 0xFF
    
    # Accept image
    if ret and key == ord('y'):
        objpoints.append(objp)
        imgpoints.append(corners)
        # Save accepted image with wireframe to output folder
        output_filename = f"output/accepted_{accepted_count:02d}.png"
        cv2.imwrite(output_filename, display)
        print(f"Accepted - Saved to {output_filename}")
        accepted_count += 1
    # Skip image
    elif key == 27:  # ESC key
        print("Skipping remaining images")
        break
    else:
        print("Rejected")

cv2.destroyAllWindows()

# Check if we have enough images
if len(objpoints) < 5:
    print(f"\nNot enough valid images. Need at least 5, got {len(objpoints)}")
    exit()

print(f"\n--- Calibrating with {len(objpoints)} images ---")

# Perform calibration
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# Calculate reprojection error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(
        objpoints[i], rvecs[i], tvecs[i], K, dist
    )
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error

mean_error /= len(objpoints)

# Print results
print("\n--- Calibration Results ---")
print("Camera Matrix (K):")
print(K)
print("\nDistortion Coefficients:")
print(dist)
print(f"\nMean Reprojection Error: {mean_error:.4f} pixels")
print("=" * 40)

# Save calibration parameters
np.savez("thermal_calibration.npz", K=K, dist=dist)
print("\nCalibration saved to: thermal_calibration.npz")