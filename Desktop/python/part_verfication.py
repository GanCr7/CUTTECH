import cv2
import numpy as np

# ---------------- CONFIG ----------------
cap = cv2.VideoCapture(0)  # Webcam

# Example points for a shape (X, Y, Z) -- you can feed any shape
shape_points = points = [
    # Polygon points
    (66.67499993, 92.07499990, 1.0),
    (44.67795469, 104.77499989, 1.0),
    (44.67795469, 130.17499987, 1.0),
    (66.67499993, 142.87499986, 1.0),
    (88.67204517, 130.17499987, 1.0),
    (88.67204517, 104.77499989, 1.0),
    (66.67499993, 92.07499990, 1.0)
]


# Convert to numpy array for OpenCV
target_pts = np.array([(x, y) for x, y, z in shape_points], np.int32).reshape((-1,1,2))

# Compute target centroid
tx = int(np.mean([x for x, y, z in shape_points]))
ty = int(np.mean([y for x, y, z in shape_points]))

# Tolerance for placement (pixels)
tolerance = 30

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for mirror view

    # --- Draw target shape ---
    cv2.polylines(frame, [target_pts], isClosed=True, color=(0,0,255), thickness=2)  # Red initially

    # --- Detect shapes held by toddler ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    closest_dist = float('inf')
    shape_centroid = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:  # Ignore small noise
            continue

        # Centroid
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Distance to target
        dist = np.sqrt((cx-tx)**2 + (cy-ty)**2)
        if dist < closest_dist:
            closest_dist = dist
            shape_centroid = (cx, cy)

    # --- Provide feedback ---
    if shape_centroid:
        # Draw current shape position
        cv2.circle(frame, shape_centroid, 5, (255,0,0), -1)
        # Distance info
        cv2.putText(frame, f"dx: {shape_centroid[0]-tx}, dy: {shape_centroid[1]-ty}",
                    (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        # Change outline color if close enough
        if closest_dist < tolerance:
            cv2.polylines(frame, [target_pts], isClosed=True, color=(0,255,0), thickness=3)
            cv2.putText(frame, "Perfect!", (tx-40, ty-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # Show frame
    cv2.imshow("Shape Placement Game", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()