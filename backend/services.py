import os
import csv
import time
import random
from datetime import datetime
import numpy as np

# הגדרת נתיב הנתונים בתוך הקונטיינר
# ודא שב-docker-compose.yml מוגדר ה-Volume המתאים
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def init_csv_file(label):
    """יוצר קובץ CSV חדש עם שם מפורט: תרגיל_תאריך_שעה_מזהה"""
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_id = random.randint(1000, 9999)
    
    file_name = f"{label}_{now}_{unique_id}.csv"
    file_path = os.path.join(DATA_DIR, file_name)
    
    headers = ['label', 'timestamp']
    for i in range(33):
        # הוספנו פה את v_{i} בסוף
        headers.extend([f'x_{i}', f'y_{i}', f'z_{i}', f'v_{i}'])
        
    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
    return file_path

def append_to_csv(file_path, label, landmarks_list):
    """כותב שורת נתונים לקובץ ה-CSV הקיים"""
    # landmarks_list מגיע מהדפדפן כרשימה שטוחה [x0, y0, z0, v0, x1...]
    row = [label, time.time()] + landmarks_list
    
    with open(file_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def calculate_angle(a, b, c):
    """מחשב זווית בין שלוש נקודות (משמש לפידבק בזמן אמת)"""
    a = np.array([a['x'], a['y']])
    b = np.array([b['x'], b['y']])
    c = np.array([c['x'], c['y']])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)