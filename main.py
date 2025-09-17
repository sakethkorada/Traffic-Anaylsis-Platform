# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from ultralytics import YOLO
import boto3
import pandas as pd
import io
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# --- Initialization ---
model = YOLO('yolov8n.pt')
app = FastAPI()
s3_client = boto3.client('s3', region_name=REGION_NAME)

class ImagePath(BaseModel):
    path: str

@app.post("/infer")
def infer(image: ImagePath):
    results = model(image.path)
    
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "class_id": int(box.cls),
                "class_name": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "box_x1": float(box.xyxy[0][0]),
                "box_y1": float(box.xyxy[0][1]),
                "box_x2": float(box.xyxy[0][2]),
                "box_y2": float(box.xyxy[0][3]),
            })
    
    # --- S3 Upload Logic ---
    if detections:
        df = pd.DataFrame(detections)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        
        now = datetime.utcnow()
        s3_key = f"detections/year={now.year}/month={now.month:02d}/day={now.day:02d}/{now.strftime('%Y%m%d_%H%M%S')}.parquet"
        
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=parquet_buffer.getvalue())
        
        return {"status": "success", "s3_key": s3_key, "detections_count": len(detections)}
        
    return {"status": "success", "detections_count": 0}