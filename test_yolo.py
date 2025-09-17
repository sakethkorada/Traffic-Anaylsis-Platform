# test_yolo.py
from ultralytics import YOLO
import torch

# Check if GPU is available
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.get_device_name(0)}")

# Load a pretrained YOLOv8 model
model = YOLO('yolov8n.pt')  # 'n' is for the small "nano" model

# Run inference on a test image (use any image with cars or people)
results = model('https://ultralytics.com/images/bus.jpg')

# Show the results
for r in results:
    r.show() # This will display the image with detections

print("Inference complete. Check the displayed image.")