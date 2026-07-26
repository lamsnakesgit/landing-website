import cv2
import numpy as np

img = cv2.imread('/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/media__1784922984008.jpg')
print("Image shape:", img.shape)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Cyan color range in OpenCV (H: 0-180, S: 0-255, V: 0-255)
# Cyan is ~180 degrees in standard HSV, so ~90 in OpenCV. 
# We'll use 80 to 100.
lower_cyan = np.array([80, 50, 50])
upper_cyan = np.array([100, 255, 255])

mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)

# Find contours of cyan regions
contours, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

best_rect = None
max_area = 0
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h
    if area > max_area and w > 200 and h > 20 and h < 200: # Typical banner dimensions
        max_area = area
        best_rect = (x, y, w, h)

print("Best cyan banner rect (x, y, w, h):", best_rect)
