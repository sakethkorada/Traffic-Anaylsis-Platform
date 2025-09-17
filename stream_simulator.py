# stream_simulator.py
import cv2
import requests
import time
import os
import boto3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
VIDEO_PATH = "test.mp4" 
INFERENCE_API_URL = os.getenv("INFERENCE_API_URL")
FRAME_OUTPUT_DIR = "images"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")
MAX_WORKERS = 10 # Number of parallel uploads

# --- Setup ---
if not os.path.exists(FRAME_OUTPUT_DIR):
    os.makedirs(FRAME_OUTPUT_DIR)
s3_client = boto3.client('s3', region_name=REGION_NAME)

def upload_and_process(frame_data):
    """Function to be run in a separate thread."""
    frame_count, frame = frame_data
    
    frame_filename = f"frame_{frame_count:04d}.jpg"
    local_frame_path = os.path.join(FRAME_OUTPUT_DIR, frame_filename)
    cv2.imwrite(local_frame_path, frame)
    
    s3_image_key = f"images/{frame_filename}"
    
    try:
        s3_client.upload_file(local_frame_path, S3_BUCKET_NAME, s3_image_key)
        
        response = requests.post(INFERENCE_API_URL, json={"path": s3_image_key})
        response.raise_for_status()
        
        # This will now print out of order, which is fine
        # print(f"Frame {frame_count}: Processed with result: {response.json()}")

    except Exception as e:
        print(f"Error processing frame {frame_count}: {e}")

# --- Main Loop ---
vid = cv2.VideoCapture(VIDEO_PATH)
frame_count = 0
start_time = time.time()

# Create a thread pool to manage parallel uploads
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    while True:
        success, frame = vid.read()
        if not success:
            break
        
        frame_count += 1
        
        # Submit the upload/processing task to the thread pool
        executor.submit(upload_and_process, (frame_count, frame))

        if frame_count % 20 == 0:
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            print(f"--- Frames submitted to queue: {frame_count}, Approx submission FPS: {fps:.2f} ---")

print("All frames have been submitted to the processing queue.")