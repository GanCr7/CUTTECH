# # import cv2
# # import numpy as np

# # # =========================
# # # Shape Data Class
# # # =========================
# # class Shape:
# #     def __init__(self, shape_type, area, perimeter, cx, cy, contour):
# #         self.shape_type = shape_type
# #         self.area = area
# #         self.perimeter = perimeter
# #         self.cx = cx
# #         self.cy = cy
# #         self.contour = contour

# # # =========================
# # # Morphology helpers
# # # =========================
# # def closing(mask):
# #     kernel = np.ones((5, 5), np.uint8)
# #     return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# # def opening(mask):
# #     kernel = np.ones((5, 5), np.uint8)
# #     return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# # # =========================
# # # Shape detection function
# # # =========================
# # def detect_shapes(frame):
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# #     # Use Canny for better edge detection
# #     edges = cv2.Canny(gray, 50, 150)
# #     edges = closing(edges)
# #     edges = opening(edges)

# #     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# #     detected_shapes = []

# #     for contour in contours:
# #         area = cv2.contourArea(contour)
# #         if area < 500:  # ignore small noise
# #             continue

# #         perimeter = cv2.arcLength(contour, True)
# #         approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
# #         cx = int(cv2.moments(contour)["m10"] / cv2.moments(contour)["m00"])
# #         cy = int(cv2.moments(contour)["m01"] / cv2.moments(contour)["m00"])
# #         edges_count = len(approx)

# #         shape_type = "Unknown"

# #         # Regular shapes
# #         if edges_count == 3:
# #             shape_type = "Triangle"
# #         elif edges_count == 4:
# #             x, y, w, h = cv2.boundingRect(approx)
# #             ar = w / float(h)
# #             shape_type = "Square" if 0.95 < ar < 1.05 else "Rectangle"
# #         elif edges_count == 5:
# #             shape_type = "Pentagon"
# #         elif edges_count == 6:
# #             shape_type = "Hexagon"
# #         else:
# #             # Check circularity for circles
# #             circularity = 4 * np.pi * area / (perimeter ** 2)
# #             if circularity > 0.75:
# #                 shape_type = "Circle"
# #             else:
# #                 # Attempt X-shape detection
# #                 # Heuristic: X-shape often has 8 vertices or diagonal cross
# #                 if edges_count == 8 or check_x_shape(contour):
# #                     shape_type = "X-Shape"

# #         detected_shapes.append(Shape(shape_type, area, perimeter, cx, cy, contour))

# #     return detected_shapes

# # # =========================
# # # Heuristic X-shape detection
# # # =========================
# # def check_x_shape(contour):
# #     # Fit bounding rectangle and check if diagonal lines cross
# #     x, y, w, h = cv2.boundingRect(contour)
# #     rect_area = w * h
# #     contour_area = cv2.contourArea(contour)
# #     # If area of contour is roughly half of bounding rect, likely an X
# #     if 0.4 < contour_area / rect_area < 0.6:
# #         return True
# #     return False

# # # =========================
# # # Main webcam loop
# # # =========================
# # def main():
# #     cap = cv2.VideoCapture(0)
# #     if not cap.isOpened():
# #         print("❌ Cannot open webcam")
# #         return

# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break

# #         shapes = detect_shapes(frame)

# #         for s in shapes:
# #             cv2.drawContours(frame, [s.contour], -1, (0, 255, 0), 2)
# #             cv2.circle(frame, (s.cx, s.cy), 5, (0, 0, 255), -1)
# #             cv2.putText(frame,
# #                         f"{s.shape_type}, A:{int(s.area)}, P:{int(s.perimeter)}",
# #                         (s.cx - 50, s.cy - 10),
# #                         cv2.FONT_HERSHEY_SIMPLEX,
# #                         0.5, (255, 0, 0), 1)

# #         cv2.imshow("Shape Detection & Measurement", frame)

# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break

# #     cap.release()
# #     cv2.destroyAllWindows()

# # if __name__ == "__main__":
# #     main()

# # 
# # import cv2
# # import numpy as np
# # import time

# # CAMERA_DEVICE_ID = 0
# # IMAGE_WIDTH = 320
# # IMAGE_HEIGHT = 240
# # fps = 0

# # def set_camera_properties(cap, width, height):
# #     """ Set resolution properties for the camera """
# #     cap.set(3, width)
# #     cap.set(4, height)

# # def capture_frame(cap):
# #     """ Capture a frame from the video source """
# #     ret, frame = cap.read()
# #     if not ret:
# #         raise ValueError("Failed to read a frame from the camera")
# #     return frame

# # def detect_circles(gray_frame):
# #     """ Detect circles using Hough transform and return the circles found """
# #     return cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1.2, 100)

# # def process_frame(frame):
# #     """ Blur, convert to grayscale and detect circles """
# #     frame = cv2.blur(frame, (3, 3))
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #     circles = detect_circles(gray)
# #     return frame, gray, circles

# # def draw_circles_on_frame(frame, circles):
# #     """ Draw circles and center rectangles on the given frame """
# #     output = frame.copy()
# #     if circles is not None:
# #         circles = np.round(circles[0, :]).astype("int")
# #         for (x, y, r) in circles:
# #             cv2.circle(output, (x, y), r, (0, 255, 0), 4)
# #             cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
# #     return output

# # def visualize_fps(image, fps: float) -> np.ndarray:
# #     """Overlay the FPS value onto the given image."""
# #     if len(np.shape(image)) < 3:
# #         text_color = (255, 255, 255)  # white
# #     else:
# #         text_color = (0, 255, 0)  # green
    
# #     row_size = 20  # pixels
# #     left_margin = 24  # pixels
# #     font_size = 1
# #     font_thickness = 1
    
# #     fps_text = 'FPS: {:.1f}'.format(fps)
# #     text_location = (left_margin, row_size)
# #     cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
# #                 font_size, text_color, font_thickness)

# #     return image

# # def main():
# #     try:
# #         cap = cv2.VideoCapture(CAMERA_DEVICE_ID)
# #         if not cap.isOpened():
# #             raise ValueError("Could not open the camera")
# #         set_camera_properties(cap, IMAGE_WIDTH, IMAGE_HEIGHT)

# #         print("Press 'Esc' to exit...")
        
# #         fps = 0  # Initialize the fps variable

# #         while True:
# #             start_time = time.time()
            
# #             frame = capture_frame(cap)
# #             frame, _, circles = process_frame(frame)
# #             output = draw_circles_on_frame(frame, circles)

# #             end_time = time.time()
# #             seconds = end_time - start_time
# #             fps = 1.0 / seconds

# #             # Overlay FPS and display frames
# #             cv2.imshow("Frame", np.hstack([visualize_fps(frame, fps), visualize_fps(output, fps)]))

# #             if cv2.waitKey(33) == 27:  # Escape key
# #                 break

# #     except Exception as e:
# #         print(e)

# #     finally:
# #         cv2.destroyAllWindows()
# #         cap.release()

# # if __name__ == "__main__":
# #     main()

# # import cv2
# # import numpy as np

# # # ---------------- CONFIG ----------------
# # cap = cv2.VideoCapture(0)  # Webcam

# # # Example points for a shape (X, Y, Z) -- you can feed any shape
# # shape_points = [
# #     (200, 100, 0),
# #     (300, 100, 0),
# #     (300, 200, 0),
# #     (200, 200, 0)
# # ]

# # # Convert to numpy array for OpenCV
# # target_pts = np.array([(x, y) for x, y, z in shape_points], np.int32).reshape((-1,1,2))

# # # Compute target centroid
# # tx = int(np.mean([x for x, y, z in shape_points]))
# # ty = int(np.mean([y for x, y, z in shape_points]))

# # # Tolerance for placement (pixels)
# # tolerance = 30

# # # ---------------- MAIN LOOP ----------------
# # while True:
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     frame = cv2.flip(frame, 1)  # Flip for mirror view

# #     # --- Draw target shape ---
# #     cv2.polylines(frame, [target_pts], isClosed=True, color=(0,0,255), thickness=2)  # Red initially

# #     # --- Detect shapes held by toddler ---
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #     blur = cv2.GaussianBlur(gray, (5,5), 0)
# #     edges = cv2.Canny(blur, 50, 150)
# #     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# #     closest_dist = float('inf')
# #     shape_centroid = None

# #     for cnt in contours:
# #         area = cv2.contourArea(cnt)
# #         if area < 500:  # Ignore small noise
# #             continue

# #         # Centroid
# #         M = cv2.moments(cnt)
# #         if M["m00"] == 0:
# #             continue
# #         cx = int(M["m10"] / M["m00"])
# #         cy = int(M["m01"] / M["m00"])

# #         # Distance to target
# #         dist = np.sqrt((cx-tx)**2 + (cy-ty)**2)
# #         if dist < closest_dist:
# #             closest_dist = dist
# #             shape_centroid = (cx, cy)

# #     # --- Provide feedback ---
# #     if shape_centroid:
# #         # Draw current shape position
# #         cv2.circle(frame, shape_centroid, 5, (255,0,0), -1)
# #         # Distance info
# #         cv2.putText(frame, f"dx: {shape_centroid[0]-tx}, dy: {shape_centroid[1]-ty}",
# #                     (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
# #         # Change outline color if close enough
# #         if closest_dist < tolerance:
# #             cv2.polylines(frame, [target_pts], isClosed=True, color=(0,255,0), thickness=3)
# #             cv2.putText(frame, "Perfect!", (tx-40, ty-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

# #     # Show frame
# #     cv2.imshow("Shape Placement Game", frame)

# #     # Exit on 'q'
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()


# # import cv2
# # import numpy as np

# # # ---------------- MANUAL SHAPE DATA ----------------
# # shapes = [
# #     # Shape from L41
# #     [
# #         (431.41899957, 123.87273902, 0.0),
# #         (399.25960626, 68.17103586, 0.0),
# #         (366.22765127, 49.01027237, 0.0),
# #         (431.41899956, 161.92499983, 0.0),
# #         (431.41899957, 123.87273902, 0.0)
# #     ],
# #     # Shape from Step71
# #     [
# #         (415.29399958, 68.51249993, 0.0),
# #         (403.41159996, 68.51249993, 0.0),
# #         (431.41899956, 117.02273903, 0.0),
# #         (431.41899956, 78.03749992, 0.0),
# #         (415.29399958, 78.03749992, 0.0),
# #         (415.29399958, 68.51249993, 0.0)
# #     ],
# #     # Shape from Step72
# #     [
# #         (415.29399958, 68.51249993, 0.0),
# #         (403.41159996, 68.51249993, 0.0),
# #         (431.41899956, 117.02273903, 0.0),
# #         (431.41899956, 78.03749992, 0.0),
# #         (415.29399958, 78.03749992, 0.0),
# #         (415.29399958, 68.51249993, 0.0)
# #     ]
# # ]

# # tolerance = 30  # pixels

# # # ---------------- HELPER FUNCTION ----------------
# # def draw_shape(frame, points, color=(0,0,255)):
# #     pts = np.array([(int(x), int(y)) for x, y, z in points], np.int32)
# #     pts = pts.reshape((-1,1,2))
# #     cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
# #     # Centroid
# #     cx = int(np.mean([x for x, y, z in points]))
# #     cy = int(np.mean([y for x, y, z in points]))
# #     cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)
# #     return (cx, cy)

# # # ---------------- MAIN LOOP ----------------
# # cap = cv2.VideoCapture(0)
# # current_shape_index = 0

# # while True:
# #     ret, frame = cap.read()
# #     if not ret:
# #         break
# #     frame = cv2.flip(frame, 1)

# #     if current_shape_index >= len(shapes):
# #         cv2.putText(frame, "All Shapes Completed!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
# #         cv2.imshow("Shape Game", frame)
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #         continue

# #     target_points = shapes[current_shape_index]
# #     tx = int(np.mean([x for x, y, z in target_points]))
# #     ty = int(np.mean([y for x, y, z in target_points]))

# #     # --- Edge Detection ---
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #     blur = cv2.GaussianBlur(gray, (5,5), 0)
# #     edges = cv2.Canny(blur, 50, 150)

# #     # Overlay edges in green
# #     edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
# #     edges_colored[np.where((edges_colored==[255,255,255]).all(axis=2))] = [0,255,0]
# #     frame = cv2.addWeighted(frame, 0.8, edges_colored, 0.8, 0)

# #     # --- Detect contours for centroid ---
# #     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# #     closest_dist = float('inf')
# #     shape_centroid = None

# #     for cnt in contours:
# #         area = cv2.contourArea(cnt)
# #         if area < 500:
# #             continue
# #         M = cv2.moments(cnt)
# #         if M['m00'] == 0:
# #             continue
# #         cx = int(M['m10']/M['m00'])
# #         cy = int(M['m01']/M['m00'])
# #         dist = np.sqrt((cx-tx)**2 + (cy-ty)**2)
# #         if dist < closest_dist:
# #             closest_dist = dist
# #             shape_centroid = (cx, cy)

# #     # --- Draw target shape ---
# #     target_color = (0,255,0) if closest_dist < tolerance else (0,0,255)
# #     draw_shape(frame, target_points, color=target_color)

# #     # --- Draw centroid info ---
# #     if shape_centroid:
# #         cv2.circle(frame, shape_centroid, 5, (255,0,0), -1)
# #         cv2.putText(frame, f"dx:{shape_centroid[0]-tx}, dy:{shape_centroid[1]-ty}", (10,30),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
# #         if closest_dist < tolerance:
# #             cv2.putText(frame, "Perfect!", (tx-40, ty-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
# #             current_shape_index += 1

# #     cv2.imshow("Shape Game", frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()

# # import cv2
# # import numpy as np

# # # ---------------- CONFIG ----------------
# # cap = cv2.VideoCapture(0)  # Webcam

# # # Example points for a shape (X, Y, Z)
# # shape_points = [
# #     (200, 100, 0),
# #     (300, 100, 0),
# #     (300, 200, 0),
# #     (200, 200, 0)
# # ]

# # # Convert to numpy array for OpenCV
# # target_pts = np.array([(x, y) for x, y, z in shape_points], np.int32).reshape((-1,1,2))

# # # Compute target centroid
# # tx = int(np.mean([x for x, y, z in shape_points]))
# # ty = int(np.mean([y for x, y, z in shape_points]))

# # # Hard threshold for correct placement (in pixels, adjust according to camera distance)
# # placement_tolerance = 50  # Example: corresponds to ~6 feet in your setup

# # # ---------------- MAIN LOOP ----------------
# # while True:
# #     ret, frame = cap.read()
# #     if not ret:
# #         break
# #     frame = cv2.flip(frame, 1)

# #     # --- Draw target shape outline (always visible) ---
# #     cv2.polylines(frame, [target_pts], isClosed=True, color=(0,0,255), thickness=2)

# #     # --- Convert to grayscale and detect object edges (robust to light) ---
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #     thresh = cv2.adaptiveThreshold(gray, 255,
# #                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
# #                                    cv2.THRESH_BINARY_INV,
# #                                    11, 2)
# #     kernel = np.ones((3,3), np.uint8)
# #     thresh = cv2.dilate(thresh, kernel, iterations=1)

# #     # --- Find largest contour (object held by toddler) ---
# #     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# #     largest_centroid = None
# #     largest_area = 0

# #     for cnt in contours:
# #         area = cv2.contourArea(cnt)
# #         if area > largest_area:
# #             M = cv2.moments(cnt)
# #             if M["m00"] == 0:
# #                 continue
# #             cx = int(M["m10"]/M["m00"])
# #             cy = int(M["m01"]/M["m00"])
# #             largest_centroid = (cx, cy)
# #             largest_area = area

# #     # --- Check placement accuracy ---
# #     if largest_centroid:
# #         # Draw a small blue dot for detected object
# #         cv2.circle(frame, largest_centroid, 5, (255,0,0), -1)

# #         # Euclidean distance to target
# #         dist = np.sqrt((largest_centroid[0]-tx)**2 + (largest_centroid[1]-ty)**2)

# #         # If within your "hard distance" tolerance, show perfect
# #         if dist < placement_tolerance:
# #             cv2.putText(frame, "Perfect!", (tx-40, ty-10),
# #                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

# #     # --- Show frame ---
# #     cv2.imshow("Shape Placement Game", frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()
# import cv2
# import numpy as np

# # --- Camera calibration (replace with your values) ---
# camera_matrix = np.array([
#     [800, 0, 320],
#     [0, 800, 240],
#     [0, 0, 1]
# ], dtype=np.float32)

# dist_coeffs = np.zeros((5, 1))  # assuming no distortion

# # --- Marker parameters ---
# MARKER_SIZE = 0.05  # meters
# aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
# parameters = cv2.aruco.DetectorParameters()

# cap = cv2.VideoCapture(0)

# # --- 3D cube points relative to marker center ---
# cube_size = MARKER_SIZE
# cube_points = np.array([
#     [0, 0, 0],
#     [cube_size, 0, 0],
#     [cube_size, cube_size, 0],
#     [0, cube_size, 0],
#     [0, 0, -cube_size],
#     [cube_size, 0, -cube_size],
#     [cube_size, cube_size, -cube_size],
#     [0, cube_size, -cube_size]
# ], dtype=np.float32)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

#     if ids is not None:
#         rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_SIZE, camera_matrix, dist_coeffs)

#         for i in range(len(ids)):
#             # Draw marker axis
#             cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.03)

#             # Draw 3D cube
#             img_pts, _ = cv2.projectPoints(cube_points, rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
#             img_pts = img_pts.reshape(-1, 2).astype(int)

#             # Base square
#             cv2.drawContours(frame, [img_pts[:4]], -1, (0, 255, 0), 2)
#             # Top square
#             cv2.drawContours(frame, [img_pts[4:]], -1, (0, 0, 255), 2)
#             # Vertical lines
#             for j in range(4):
#                 cv2.line(frame, tuple(img_pts[j]), tuple(img_pts[j + 4]), (255, 0, 0), 2)

#             # Position overlay
#             x, y, z = tvecs[i][0]
#             text_pos = f"Pos: x={x:.2f} y={y:.2f} z={z:.2f} m"
#             cv2.putText(frame, text_pos, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#     cv2.imshow("3D Cube Pose Estimation", frame)

#     if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
#         break

# cap.release()
# cv2.destroyAllWindows()


# import cv2
# import numpy as np

# # --- Camera calibration ---
# camera_matrix = np.array([
#     [800, 0, 320],
#     [0, 800, 240],
#     [0, 0, 1]
# ], dtype=np.float32)

# dist_coeffs = np.zeros((5, 1))

# # --- Marker parameters ---
# MARKER_SIZE = 0.05  # meters
# aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
# parameters = cv2.aruco.DetectorParameters()

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     corners, ids, _ = cv2.aruco.detectMarkers(
#         gray, aruco_dict, parameters=parameters
#     )

#     if ids is not None:
#         rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
#             corners, MARKER_SIZE, camera_matrix, dist_coeffs
#         )

#         for i in range(len(ids)):
#             # Draw X Y Z orientation axes only
#             cv2.drawFrameAxes(
#                 frame,
#                 camera_matrix,
#                 dist_coeffs,
#                 rvecs[i],
#                 tvecs[i],
#                 0.04  # axis length (meters)
#             )

#             # Show translation values
#             x, y, z = tvecs[i][0]
#             text = f"x={x:.2f} y={y:.2f} z={z:.2f} m"
#             cv2.putText(
#                 frame, text, (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6,
#                 (0, 255, 0), 2
#             )

#     cv2.imshow("ArUco Orientation (XYZ)", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
import numpy as np

# ---------------- Camera calibration ----------------
camera_matrix = np.array([
    [800, 0, 320],
    [0, 800, 240],
    [0,   0,   1]
], dtype=np.float32)
dist_coeffs = np.zeros((5, 1))

# ---------------- Bottle dimensions (meters) ----------------
W, D, H = 0.10, 0.10, 0.20
object_points = np.array([
    [-W/2, -D/2, 0],
    [ W/2, -D/2, 0],
    [ W/2,  D/2, 0],
    [-W/2,  D/2, 0],
    [-W/2, -D/2, H],
    [ W/2, -D/2, H],
    [ W/2,  D/2, H],
    [-W/2,  D/2, H]
], dtype=np.float32)

# ---------------- ArUco setup ----------------
MARKER_SIZE = 0.05  # 5 cm
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -------- Detect ArUco --------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, MARKER_SIZE, camera_matrix, dist_coeffs
        )
        # Draw each marker
        for i in range(len(ids)):
            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.04)

    # -------- Detect Blue Bottle --------
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 80, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 1500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

            # 2D image points from bounding box
            image_points = np.array([
                [x,     y+h],   # bottom-left
                [x+w,   y+h],   # bottom-right
                [x+w,   y],     # top-right
                [x,     y],     # top-left
                [x,     y+h],   # duplicate
                [x+w,   y+h]
            ], dtype=np.float32)

            # Corresponding 3D points
            model_points = np.array([
                [-W/2, -D/2, 0],
                [ W/2, -D/2, 0],
                [ W/2,  D/2, H],
                [-W/2,  D/2, H],
                [-W/2, -D/2, 0],
                [ W/2, -D/2, 0]
            ], dtype=np.float32)

            success, rvec_b, tvec_b = cv2.solvePnP(
                model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                # Draw bottle axes
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec_b, tvec_b, 0.08)

                x3d, y3d, z3d = tvec_b.ravel()
                cv2.putText(frame, f"Bottle XYZ (cam): {x3d:.2f}, {y3d:.2f}, {z3d:.2f} m",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                # -------- Bottle relative to first detected ArUco --------
                if ids is not None:
                    R_m, _ = cv2.Rodrigues(rvecs[0])
                    t_m = tvecs[0].reshape(3,1)

                    R_b, _ = cv2.Rodrigues(rvec_b)
                    t_b = tvec_b.reshape(3,1)

                    # Transform bottle to marker frame
                    t_bottle_marker = R_m.T @ (t_b - t_m)
                    R_bottle_marker = R_m.T @ R_b
                    rvec_b_marker, _ = cv2.Rodrigues(R_bottle_marker)

                    x_m, y_m, z_m = t_bottle_marker.ravel()
                    cv2.putText(frame,
                                f"Bottle XYZ (marker): {x_m:.2f}, {y_m:.2f}, {z_m:.2f} m",
                                (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

                    # Draw axes in camera frame (based on marker frame)
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec_b_marker, t_m + R_m @ t_bottle_marker, 0.08)

    cv2.imshow("Bottle + ArUco", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
