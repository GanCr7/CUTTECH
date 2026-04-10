import cv2
import numpy as np

# ================= CONFIG =================
MARKER_SIZE = 3.9  # cm (real marker size)

# ⚠️ Replace with real calibration for best accuracy
fx = fy = 800
cx = 320
cy = 240

camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
], dtype=float)

dist_coeffs = np.zeros((5, 1))


# ================= ARUCO SCALE =================
def get_scale_from_pose(corners):
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
        corners,
        MARKER_SIZE,
        camera_matrix,
        dist_coeffs
    )

    # Distance from camera (Z axis in cm)
    z_distance = tvecs[0][0][2]

    # Focal length
    fx = camera_matrix[0][0]

    # Scale: cm per pixel
    scale = z_distance / fx

    return scale, rvecs, tvecs


# ================= BLUE OBJECT DETECTION =================
def detect_blue_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 120, 50])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Noise cleaning
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, mask

    contour = max(contours, key=cv2.contourArea)

    if cv2.contourArea(contour) < 500:
        return None, mask

    return contour, mask


# ================= MAIN =================
def main():
    cap = cv2.VideoCapture(0)

    aruco_dict = cv2.aruco.getPredefinedDictionary(
        cv2.aruco.DICT_4X4_50
    )
    detector = cv2.aruco.ArucoDetector(aruco_dict)

    scale = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # -------- ARUCO DETECTION --------
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners)

            scale, rvecs, tvecs = get_scale_from_pose(corners)

            # Draw 3D axis
            cv2.drawFrameAxes(
                frame,
                camera_matrix,
                dist_coeffs,
                rvecs[0],
                tvecs[0],
                3
            )

            z = tvecs[0][0][2]

            cv2.putText(frame, f"Distance: {z:.2f} cm",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

            cv2.putText(frame, f"Scale: {scale:.4f} cm/pixel",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        # -------- BLUE OBJECT DETECTION --------
        contour, mask = detect_blue_object(frame)

        if contour is not None and scale is not None:
            x, y, w, h = cv2.boundingRect(contour)

            # Convert to real-world units
            width_cm = w * scale
            height_cm = h * scale
            area_cm2 = width_cm * height_cm

            # Draw contour + box
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (255, 0, 0), 2)

            # Display measurements
            text = f"W: {width_cm:.2f} cm  H: {height_cm:.2f} cm"
            cv2.putText(frame, text,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (240, 3, 252), 2)

            print(
                f"Width: {width_cm:.2f} cm | "
                f"Height: {height_cm:.2f} cm | "
                f"Area: {area_cm2:.2f} cm^2"
            )

        # -------- DISPLAY --------
        cv2.imshow("Measurement", frame)
        cv2.imshow("Blue Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# ================= RUN =================
if __name__ == "__main__":
    main()