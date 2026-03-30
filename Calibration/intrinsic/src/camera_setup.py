import cv2
import numpy as np
import os

# Try to find and open camera
camera_port = None
for i in range(8):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        camera_port = i
        print(f"Camera found at port: {i}")
        break
    cap.release()

if camera_port is None:
    print("No camera found")
    exit()

cap = cv2.VideoCapture(camera_port)

# Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

print("Camera stream started")
print("Press 's' to save frame, 'q' to quit")

frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to read frame")
        break
    
    # Normalize thermal image for display
    normalized = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
    display = np.uint8(normalized)
    
    # Add minimal UI text
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
print(f"Saved {frame_count} frames to data/ folder")