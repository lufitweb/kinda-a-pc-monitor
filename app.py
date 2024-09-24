import psutil
import GPUtil
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_size(bytes):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}B"
        bytes /= factor

def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    gpus = GPUtil.getGPUs()
    gpu_percent = gpus[0].load * 100 if gpus else 0

    system_info = {
        'cpu': cpu_percent,
        'gpu': gpu_percent,
        'ram': memory_percent,
        'disk': disk_percent
    }
    print(f"Sending system info: {system_info}")
    return system_info

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('request_update')
def handle_update_request():
    while True:
        system_info = get_system_info()
        socketio.emit('system_info', json.dumps(system_info))
        socketio.sleep(2)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)