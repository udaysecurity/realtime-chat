from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

online_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(username):
    online_users[session.sid] = username
    emit('user_list', list(online_users.values()), broadcast=True)
    emit('system_message', f"{username} joined the chat", broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    india = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(india).strftime("%I:%M %p")
    data['time'] = current_time
    emit('receive_message', data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    sid = session.sid
    if sid in online_users:
        username = online_users.pop(sid)
        emit('user_list', list(online_users.values()), broadcast=True)
        emit('system_message', f"{username} left the chat", broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)