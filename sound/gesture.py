#! /venv
import torch
import cv2
import numpy as np
from torchvision import transforms

# Load YOLOv5 model (you can change to 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x' for different sizes)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Function to perform hand gesture detection
def detect_hand_gestures(frame):
    # Perform detection
    results = model(frame)
    
    # Process results
    detections = results.xyxy[0].numpy()
    
    # Draw bounding boxes and labels on the frame
    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        if conf > 0.5:  # Confidence threshold
            label = f'{model.names[int(cls)]} {conf:.2f}'
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    return frame

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect hand gestures in the frame
    frame = detect_hand_gestures(frame)
    
    # Display the frame with detections
    cv2.imshow('Live image Detection', frame)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
