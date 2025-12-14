from flask import Flask, jsonify, render_template
import psutil

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
