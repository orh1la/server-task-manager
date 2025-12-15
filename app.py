import time
import psutil
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ------------------------
ALERT_THRESHOLD = 80        # CPU / RAM %
ALERT_DURATION = 60         # seconds
alert_start = None
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    })

@app.route("/api/processes")
def processes():
    procs = []
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
        try:
            procs.append({
                "pid": p.info['pid'],
                "name": p.info['name'],
                "cpu": p.info['cpu_percent'],
                "ram": round(p.info['memory_percent'],2)
            })
        except:
            pass
    return jsonify(sorted(procs, key=lambda x:x['cpu'], reverse=True))

@app.route("/api/auto_protect")
def auto_protect():
    global alert_start
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if cpu > ALERT_THRESHOLD or ram > ALERT_THRESHOLD:
        if alert_start is None:
            alert_start = time.time()
        elif time.time() - alert_start >= ALERT_DURATION:
            # Auto kill хамгийн их CPU идэж буй процесс
            heavy = max(psutil.process_iter(['pid','cpu_percent','memory_percent','name']),
                        key=lambda p: p.info['cpu_percent'])
            try:
                heavy.terminate()
                alert_start = None
                return jsonify({"status":"ALERT","action":"KILLED","process":heavy.info['name']})
            except:
                return jsonify({"status":"ALERT","action":"FAILED"})
        return jsonify({"status":"ALERT","action":"WAITING"})
    else:
        alert_start = None
        return jsonify({"status":"OK","action":"NONE"})

# Render-ийн хувьд
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

