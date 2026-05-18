import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, request, redirect, url_for, session
import socketio
from sockets import register_handlers

base_dir = os.path.dirname(os.path.abspath(__file__))
flask_app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

# הגדרות אבטחה
flask_app.secret_key = "super_secret_physioguide_key"
ADMIN_PASSWORD = "colman_admin_2026"

# הגדרת שרת ה-SocketIO
sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')
app = socketio.WSGIApp(sio, flask_app)

# רישום ה-Handlers מקובץ ה-sockets
register_handlers(sio)

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('recorder'))
        else:
            error = "סיסמה שגויה"
    return render_template('login.html', error=error)

@flask_app.route('/recorder')
def recorder():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('recorder.html')

if __name__ == '__main__':
    # האזנה על 0.0.0.0 כדי לאפשר גישה מחוץ לדוקר
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)