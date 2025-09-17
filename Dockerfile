#Dockerfile

FROM  python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

CMD ["uvicorn", "main:app","--host","0.0.0.0","--port", "80"]

