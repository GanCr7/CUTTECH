import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load model from Teachable Machine
model = load_model(
    r"C:\Users\CuttechPC-1\Downloads\converted_keras\keras_model.h5",
    compile=False
)

# Load labels
class_names = open(
    r"C:\Users\CuttechPC-1\Downloads\converted_keras\labels.txt",
    "r"
).readlines()

# Start webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot access webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Get frame size
    h, w, _ = frame.shape

    # Draw center detection box
    x1, y1 = int(w * 0.25), int(h * 0.25)
    x2, y2 = int(w * 0.75), int(h * 0.75)

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Crop region of interest (optional but improves accuracy)
    roi = frame[y1:y2, x1:x2]

    # Resize for model
    image_resized = cv2.resize(roi, (224, 224), interpolation=cv2.INTER_AREA)

    # Convert to array
    image_array = np.asarray(image_resized)

    # Normalize (-1 to 1)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Prepare input
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Predict
    prediction = model.predict(data, verbose=0)
    index = np.argmax(prediction)

    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]

    # Display text
    text = f"{class_name} ({confidence_score:.2f})"

    cv2.putText(frame, text, (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    # Show window
    cv2.imshow("Steel Detection", frame)

    # Exit on ESC
    if cv2.waitKey(1) == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()