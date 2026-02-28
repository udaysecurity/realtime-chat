from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

online_users = set()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(username):
    online_users.add(username)
    emit('user_list', list(online_users), broadcast=True)
    emit('system_message', f"{username} joined the chat", broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    data['time'] = datetime.now().strftime("%H:%M")
    emit('receive_message', data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # username will be handled from frontend removal
    pass

@socketio.on('leave')
def handle_leave(username):
    if username in online_users:
        online_users.remove(username)
        emit('user_list', list(online_users), broadcast=True)
        emit('system_message', f"{username} left the chat", broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)