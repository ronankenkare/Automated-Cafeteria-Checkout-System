import torch
from yolov5.models.common import DetectMultiBackend
from pathlib import Path
import cv2

# Load YOLOv5 Model
model_path = "yolov5s.pt"  # Use YOLOv5s pretrained model (replace with your custom model if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DetectMultiBackend(weights=model_path, device=device)

# Define the labels for the food items you want to detect
# These are class IDs from the COCO dataset. Add more if needed.
food_labels = {
    46: "apple",
    47: "banana",
    48: "sandwich",
    54: "pizza",
    50: "orange"
}

# Initialize the AI camera
camera = cv2.VideoCapture(0)  # Adjust the index if needed
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# Detection Loop
try:
    while True:
        # Capture a frame
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Convert the frame to the YOLOv5 input format
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(img, size=640)  # Resize the frame to 640x640 for YOLOv5

        # Parse detections
        detections = results.xyxy[0].cpu().numpy()  # Bounding boxes, confidence, class
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            cls = int(cls)
            if cls in food_labels:
                label = food_labels[cls]
                # Draw the bounding box and label on the frame
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({conf:.2f})", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Food Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
