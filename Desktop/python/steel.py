import cv2
import numpy as np

# ================= CONFIG =================
MARKER_SIZE = 9.7  # cm

fx = fy = 800
cx = 320
cy = 240

camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
], dtype=float)

dist_coeffs = np.zeros((5, 1))


# ================= ARUCO =================
def get_scale_from_pose(corners):
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
        corners, MARKER_SIZE, camera_matrix, dist_coeffs
    )
    z = tvecs[0][0][2]
    fx = camera_matrix[0][0]
    scale = z / fx
    return scale, rvecs, tvecs


# ================= STEEL DETECTION =================
def detect_stainless_steel(frame):

    # ---------- HSV (low saturation) ----------
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_hsv = cv2.inRange(
        hsv,
        np.array([0, 0, 70]),
        np.array([179, 50, 255])
    )

    # ---------- RGB gray detection ----------
    b, g, r = cv2.split(frame)
    diff_rg = cv2.absdiff(r, g)
    diff_gb = cv2.absdiff(g, b)
    diff_rb = cv2.absdiff(r, b)

    mask_rgb = cv2.threshold(
        diff_rg + diff_gb + diff_rb,
        30, 255,
        cv2.THRESH_BINARY_INV
    )[1]

    # ---------- Brightness ----------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask_bright = cv2.inRange(gray, 80, 255)

    # ---------- Combine ----------
    mask = cv2.bitwise_and(mask_hsv, mask_rgb)
    mask = cv2.bitwise_and(mask, mask_bright)

    # ---------- Strong Morphology (important now) ----------
    kernel = np.ones((7, 7), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Fill holes inside object
    mask = cv2.dilate(mask, kernel, iterations=1)

    # ---------- Contours ----------
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, mask

    best = None
    max_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1500:   # increased threshold
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        if 0.3 < aspect_ratio < 3.5:
            if area > max_area:
                max_area = area
                best = cnt

    return best, mask


# ================= MAIN =================
def main():
    cap = cv2.VideoCapture(0)

    aruco_dict = cv2.aruco.getPredefinedDictionary(
        cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(aruco_dict)

    scale = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ---- ARUCO ----
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners)

            scale, rvecs, tvecs = get_scale_from_pose(corners)

            cv2.drawFrameAxes(frame, camera_matrix,
                              dist_coeffs,
                              rvecs[0], tvecs[0], 3)

        # ---- STEEL DETECTION ----
        contour, mask = detect_stainless_steel(frame)

        if contour is not None and scale is not None:
            x, y, w, h = cv2.boundingRect(contour)

            width_cm = w * scale
            height_cm = h * scale

            cv2.drawContours(frame, [contour], -1,
                             (0, 255, 0), 2)
            cv2.rectangle(frame,
                          (x, y),
                          (x + w, y + h),
                          (255, 0, 0), 2)

            cv2.putText(frame,
                        f"W:{width_cm:.2f} H:{height_cm:.2f}",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 0, 255), 2)

            print(f"Width: {width_cm:.2f} cm | Height: {height_cm:.2f} cm")

        # ---- DISPLAY ----
        cv2.imshow("Measurement", frame)
        cv2.imshow("Steel Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()