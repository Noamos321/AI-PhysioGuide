FROM python:3.9-slim

# התקנת תלויות מערכת עבור OpenCV ו-MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# העתקת קובץ הדרישות והתקנה
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת כל תוכן תיקיית ה-backend לתוך ה-Container
COPY backend/ ./backend/

# הגדרת משתנה סביבה כדי שפייתון ימצא את הקבצים
ENV PYTHONPATH=/app/backend

# הרצת השרת מתוך התיקייה החדשה
CMD ["python", "backend/app.py"]