import cv2
import numpy as np

# Configuration - modify these values as needed
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
DPI = 300  # Printer DPI

# Checkerboard pattern - modify these to change board size
ROWS = 7
COLS = 10
SQUARE_SIZE_MM = 20

# Convert mm to pixels
def mm_to_px(mm):
    return int(mm * DPI / 25.4)

# Calculate dimensions in pixels
square_px = mm_to_px(SQUARE_SIZE_MM)
img_w = mm_to_px(A4_WIDTH_MM)
img_h = mm_to_px(A4_HEIGHT_MM)

# Create white canvas
img = np.ones((img_h, img_w), dtype=np.uint8) * 255

# Center the board
board_w = COLS * square_px
board_h = ROWS * square_px
start_x = (img_w - board_w) // 2
start_y = (img_h - board_h) // 2

# Draw checkerboard pattern
for i in range(ROWS):
    for j in range(COLS):
        if (i + j) % 2 == 0:
            x1 = start_x + j * square_px
            y1 = start_y + i * square_px
            x2 = x1 + square_px
            y2 = y1 + square_px
            cv2.rectangle(img, (x1, y1), (x2, y2), 0, -1)

# Save image
cv2.imwrite("checkerboard.png", img)
print(f"Checkerboard generated: {ROWS}x{COLS} with {SQUARE_SIZE_MM}mm squares")