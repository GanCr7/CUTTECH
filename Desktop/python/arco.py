import cv2
import numpy as np

# ---------------- CONFIG ----------------
cap = cv2.VideoCapture(0)

MARKER_SIZE = 0.05  # meters (5 cm)

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

# Example shape (same as yours)
shape_points = [
    (66.67, 92.07, 1.0),
    (44.67, 104.77, 1.0),
    (44.67, 130.17, 1.0),
    (66.67, 142.87, 1.0),
    (88.67, 130.17, 1.0),
    (88.67, 104.77, 1.0),
    (66.67, 92.07, 1.0)
]

target_pts = np.array([(x, y) for x, y, z in shape_points],
                      np.int32).reshape((-1,1,2))

tx = int(np.mean([x for x, y, z in shape_points]))
ty = int(np.mean([y for x, y, z in shape_points]))

tolerance = 30

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # --- Detect ArUco markers ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco.detectMarkers(gray, dictionary, parameters=parameters)

    scale = None

    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)

        # Use first detected marker for scale
        c = corners[0][0]

        # pixel width of marker
        pixel_width = np.linalg.norm(c[0] - c[1])

        scale = MARKER_SIZE / pixel_width  # meters per pixel

    # --- Draw target shape ---
    cv2.polylines(frame, [target_pts], True, (0,0,255), 2)

    # --- Detect contours ---
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    closest_dist = float('inf')
    shape_centroid = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        dist = np.sqrt((cx-tx)**2 + (cy-ty)**2)

        if dist < closest_dist:
            closest_dist = dist
            shape_centroid = (cx, cy)

    # --- Feedback ---
    if shape_centroid:
        cx, cy = shape_centroid

        cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)

        dx = cx - tx
        dy = cy - ty

        # Convert to real units if marker detected
        if scale:
            dx_m = dx * scale
            dy_m = dy * scale

            cv2.putText(frame, f"dx: {dx_m:.3f} m", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.putText(frame, f"dy: {dy_m:.3f} m", (10,60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        else:
            cv2.putText(frame, f"dx(px): {dx}, dy(px): {dy}",
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        if closest_dist < tolerance:
            cv2.polylines(frame, [target_pts], True, (0,255,0), 3)
            cv2.putText(frame, "Perfect!", (tx-40, ty-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Shape Placement Game + Measurement", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()