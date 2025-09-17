# dashboard.py
import streamlit as st
import pandas as pd
import boto3
from PIL import Image, ImageDraw
import io
import re
import os
from dotenv import load_dotenv

load_dotenv()

# --- AWS Configuration ---
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# Initialize boto3 S3 client
s3_client = boto3.client('s3', region_name=REGION_NAME)

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("Traffic Analysis Results")

@st.cache_data # Cache the list of files to speed up app
def list_s3_files(prefix):
    """Lists files in an S3 bucket folder."""
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
    files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.parquet')]
    return files

# --- Main App Logic ---
detections_prefix = "detections/"
parquet_files = list_s3_files(detections_prefix)

if not parquet_files:
    st.warning("No detection files found in S3 bucket. Please run the simulator.")
else:
    # Let user select a file
    selected_file = st.selectbox("Select a detection file to view:", parquet_files)
    
    if selected_file:
        # --- 1. Load Detection Data ---
        s3_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=selected_file)
        df = pd.read_parquet(io.BytesIO(s3_obj['Body'].read()))
        
        # --- 2. Determine Corresponding Image Path ---
        # Heuristic: extract the frame number from the parquet filename
        # e.g., 'detections/year=.../20250916_180630.parquet' -> find a frame number
        # A more robust system would store the frame path in the parquet file itself
        # For this demo, we'll just show the first frame as an example
        image_key = "images/frame_0001.jpg" # Using a placeholder for this demo
        st.info(f"Displaying detections on a sample frame: {image_key}. A production system would link each result to its specific frame.")

        try:
            # --- 3. Load the Image ---
            s3_img_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
            image_bytes = s3_img_obj['Body'].read()
            img = Image.open(io.BytesIO(image_bytes))
            draw = ImageDraw.Draw(img)

            # --- 4. Draw Bounding Boxes ---
            for index, row in df.iterrows():
                x1, y1, x2, y2 = row['box_x1'], row['box_y1'], row['box_x2'], row['box_y2']
                label = f"{row['class_name']} ({row['confidence']:.2f})"
                draw.rectangle([(x1, y1), (x2, y2)], outline="lime", width=3)
                draw.text((x1, y1), label, fill="white")

            # --- 5. Display ---
            st.image(img, caption=f"Detections from {selected_file}", use_column_width=True)
            st.dataframe(df)

        except s3_client.exceptions.NoSuchKey:
            st.error(f"Could not find the corresponding image file '{image_key}' in the S3 bucket.")
            st.dataframe(df)