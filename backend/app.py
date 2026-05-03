import eventlet
eventlet.monkey_patch()

import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template
import socketio
import mediapipe as mp

base_dir = os.path.dirname(os.path.abspath(__file__))
flask_app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')
app = socketio.WSGIApp(sio, flask_app)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(a, b, c):
    """
    מחשב את הזווית במעלות במפרק האמצעי (b).
    a, b, c הם צמתים (landmarks) מהמודל.
    """
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

@flask_app.route('/')
def index():
    return render_template('index.html')

@sio.on('video_frame')
def handle_frame(sid, data):
    try:
        image_b64 = data.split(',')[1] if isinstance(data, str) else data['image'].split(',')[1]

        image_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = pose.process(img_rgb)

        status = "Waiting"
        message = "מחפש מתאמן..."

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # חילוץ הנקודות
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

            # חישוב זווית המרפקים
            angle_left = calculate_angle(left_shoulder, left_elbow, left_wrist)
            angle_right = calculate_angle(right_shoulder, right_elbow, right_wrist)

            # זיהוי אוטומטי של היד שעובדת (היד עם שורש כף היד הגבוה יותר = Y קטן יותר)
            if right_wrist.y < left_wrist.y:
                active_lift = right_shoulder.y - right_wrist.y
                active_wrist_y = right_wrist.y
                active_angle = angle_right
            else:
                active_lift = left_shoulder.y - left_wrist.y
                active_wrist_y = left_wrist.y
                active_angle = angle_left

            # בדיקה האם היד יחסית ישרה (מעל 160 מעלות)
            is_straight_enough = active_angle > 160

            # לוגיקת הפידבק
            if not is_straight_enough:
                status = "Incorrect"
                message = "יישר את היד במרפק! 💪"
            elif active_wrist_y < nose.y:
                status = "Correct"
                message = "מצוין! היד ישרה ומעל הראש 🌟"
            elif active_lift > 0:
                status = "Partial"
                message = "יד ישרה, עכשיו הרם מעל הראש ⬆️"
            else:
                status = "Incorrect"
                message = "הרם את היד ישרה מהצד כלפי מעלה"

        sio.emit('feedback', {'status': status, 'message': message}, room=sid)

    except Exception as e:
        print("Error processing frame:", e)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
