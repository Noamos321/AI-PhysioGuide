from services import init_csv_file, append_to_csv

# ניהול מצב ההקלטה בזיכרון השרת
RECORDING_STATE = {
    "is_recording": False,
    "label": "",
    "file_path": ""
}

def register_handlers(sio):
    
    @sio.on('start_recording')
    def handle_start_recording(sid, data):
        label = data.get('label', 'unknown')
        RECORDING_STATE['is_recording'] = True
        RECORDING_STATE['label'] = label
        RECORDING_STATE['file_path'] = init_csv_file(label)
        print(f"[SERVER] Started recording: {RECORDING_STATE['file_path']}")

    @sio.on('stop_recording')
    def handle_stop_recording(sid):
        RECORDING_STATE['is_recording'] = False
        print(f"[SERVER] Stopped recording and saved file.")

    @sio.on('pose_data')
    def handle_pose_data(sid, data):
        """מקבל נתוני שלד מהדפדפן ושומר אותם אם ההקלטה פעילה"""
        if not RECORDING_STATE['is_recording']:
            return

        landmarks = data.get('landmarks', [])
        if landmarks:
            append_to_csv(
                RECORDING_STATE['file_path'], 
                RECORDING_STATE['label'], 
                landmarks
            )