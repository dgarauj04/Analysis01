FROM python:3.11-slim

# System dependencies for pdf2image/poppler and tesseract
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libsm6 libxrender1 libxext6 libfontconfig1 \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
