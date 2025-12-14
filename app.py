import os
from flask import Flask, jsonify, render_template
import psutil

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# CPU, RAM, Disk status
@app.route('/api/status')
def status():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    })

# Process list
@app.route('/api/processes')
def processes():
    procs = []
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify(procs)

# Kill process
@app.route('/api/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()  # зөөлөн kill
        return jsonify({"status": "terminated"})
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return jsonify({"status": "failed"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

