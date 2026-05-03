FROM python:3.10-slim

# התקנת ספריות מערכת שנדרשות עבור OpenCV ו-MediaPipe בלינוקס
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# נעתיק את הקוד שנכתוב מיד
COPY . .

# נריץ את השרת בפורט 5000
EXPOSE 5000

CMD ["python", "app.py"]
