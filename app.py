from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

online_users = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file"
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return "Invalid file"


@socketio.on('join')
def handle_join():
    username = session.get('username')
    online_users[request.sid] = username
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
    sid = request.sid
    if sid in online_users:
        username = online_users.pop(sid)
        emit('user_list', list(online_users.values()), broadcast=True)
        emit('system_message', f"{username} left the chat", broadcast=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)