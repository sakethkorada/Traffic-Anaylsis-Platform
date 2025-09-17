# 🚦 Real-Time Traffic Analytics Platform

This project is a full-stack, cloud-native platform to analyze real-time video streams for traffic monitoring using computer vision and a serverless data pipeline on AWS.



---

## ✨ Features

- **Real-Time Object Detection:** Identifies cars, buses, pedestrians, etc., from a video source using a YOLOv8 model.
- **GPU-Accelerated Microservice:** The inference engine is containerized with Docker and served via a FastAPI API for high performance.
- **Asynchronous Ingestion:** A multi-threaded client simulates a high-throughput video feed, processing over 100 FPS.
- **Data Lake Storage:** Detection results are saved as partitioned Parquet files in an AWS S3 data lake.
- **Serverless Analytics:** Data is automatically cataloged with AWS Glue and can be queried using standard SQL with Amazon Athena.
- **Interactive Dashboard:** A Streamlit web app visualizes detection results by drawing bounding boxes on the corresponding video frames.

---

## 🛠️ Tech Stack & Architecture

- **Cloud:** AWS (S3, IAM, Glue, Athena, Budgets)
- **AI/ML:** PyTorch, YOLOv8, OpenCV
- **Backend:** Python, Docker, FastAPI
- **Frontend:** Streamlit, Pandas
- **Data Format:** Parquet

### Architecture Flow
`Video File` → `Simulator (Python)` → `Inference Service (Docker)` → `S3 Data Lake` → `Athena` → `Streamlit Dashboard`

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- Docker Desktop
- An AWS Account
- Configured AWS CLI with an IAM user

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Create a Python virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
    *(**Note:** Ensure your `requirements.txt` file contains all necessary packages like `ultralytics`, `torch`, `opencv-python`, `fastapi`, `boto3`, `pandas`, `pyarrow`, `streamlit`, `pillow`, and `requests`)*

3.  **AWS Setup:**
    - Create an S3 bucket and note its name and region.
    - Create a local `images` folder for the simulator to use.

---

## 🏃‍♀️ How to Run

You will need three separate terminals.

1.  **Run the Inference Server**

    In your first terminal, build the Docker image and run the container. **Remember to replace your bucket name.**

    ```powershell
    # Build the image
    docker build -t traffic-inference .

    # Run the container
    docker run -p 8000:80 --gpus all `
      -v ${PWD}/images:/app/images `
      -v ${HOME}/.aws:/root/.aws `
      -e S3_BUCKET_NAME="your-bucket-name-here" `
      traffic-inference
    ```

2.  **Run the Streamlit Dashboard**

    In your second terminal (with `venv` active), run the dashboard. A browser tab will open.

    ```powershell
    streamlit run dashboard.py
    ```

3.  **Run the Video Simulator**

    In your third terminal (with `venv` active), run the simulator to start processing the video.

    ```powershell
    python stream_simulator.py
    ```

You can now view the results in real-time on your Streamlit dashboard.
