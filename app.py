import os
from flask import Flask, jsonify, render_template
import psutil
import threading
import time

app = Flask(__name__)

# Thresholds
CPU_LIMIT = 80     # CPU %
RAM_LIMIT = 80     # RAM %
CHECK_INTERVAL = 5 # seconds
ALERT_DURATION = 1 * 60  # 1 minute

# Counter
alert_start_time = None

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
        p.terminate()
        return jsonify({"status": "terminated"})
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return jsonify({"status": "failed"}), 400

# Background monitor thread
def monitor_processes():
    global alert_start_time
    while True:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent

        # Start alert counter if threshold exceeded
        if cpu > CPU_LIMIT or ram > RAM_LIMIT:
            if alert_start_time is None:
                alert_start_time = time.time()
        else:
            alert_start_time = None

        # Auto End Task if alert > ALERT_DURATION
        if alert_start_time and (time.time() - alert_start_time) > ALERT_DURATION:
            for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
                try:
                    if p.info['name'] not in ['python', 'bash', 'systemd']:
                        p.terminate()
                        print(f"⚠️ Auto End Task: {p.info['name']} PID:{p.info['pid']} CPU:{p.info['cpu_percent']} RAM:{p.info['memory_percent']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            alert_start_time = None  # reset after auto terminate

        time.sleep(CHECK_INTERVAL)

threading.Thread(target=monitor_processes, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

