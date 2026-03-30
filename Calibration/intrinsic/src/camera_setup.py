import cv2
import numpy as np
import os

# Camera selection 
camera_port = None

print("Searching for available cameras...\n")

for i in range(8):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()

    if ret:
        print(f"Camera index {i} detected")

        # Show preview
        cv2.imshow(f"Camera {i}", frame)
        print(f"Press 'y' to select camera {i}, any other key to skip")

        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key == ord('y'):
            camera_port = i
            cap.release()
            break

    cap.release()

if camera_port is None:
    print("No camera selected")
    exit()

print(f"\nUsing camera index: {camera_port}")

# Open selected camera
cap = cv2.VideoCapture(camera_port)

if not cap.isOpened():
    print("Failed to open selected camera")
    exit()

# Create data folder
if not os.path.exists("data"):
    os.makedirs("data")

print("\nCamera stream started")
print("Press 's' to save frame, 'q' to quit")

frame_count = 0

# Capture loop
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    # Normalize thermal image for display
    normalized = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
    display = np.uint8(normalized)

    # Minimal UI text
    cv2.putText(display, f"Frames saved: {frame_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(display, "Press 's' to save, 'q' to quit", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Thermal Camera", display)

    key = cv2.waitKey(1) & 0xFF

    # Save frame
    if key == ord('s'):
        filename = f"data/frame_{frame_count:02d}.png"
        cv2.imwrite(filename, display)
        print(f"Saved: {filename}")
        frame_count += 1

    # Exit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nSaved {frame_count} frames to data/ folder")
