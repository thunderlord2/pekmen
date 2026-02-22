from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

BEST_FILE = "global_best.json"

# =========================
# Load & Save Best
# =========================
def load_best():
    if not os.path.exists(BEST_FILE):
        return {"time": float("inf"), "name": ""}
    try:
        with open(BEST_FILE, "r") as f:
            return json.load(f)
    except:
        return {"time": float("inf"), "name": ""}

def save_best(best):
    with open(BEST_FILE, "w") as f:
        json.dump(best, f)

# =========================
# Submit Time Endpoint
# =========================
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    new_time = data.get("time")
    player_name = data.get("name", "Unknown")

    if new_time is None:
        return jsonify({"error": "Missing time"}), 400

    current = load_best()

    if new_time < current["time"]:
        # New record
        best = {"time": new_time, "name": player_name}
        save_best(best)
        return jsonify({"status": "new_record", "best": best})
    else:
        return jsonify({"status": "not_record", "best": current})

# =========================
# Get Best Endpoint
# =========================
@app.route("/best", methods=["GET"])
def best():
    return jsonify(load_best())

# =========================
# Simple Homepage Display
# =========================
@app.route("/")
def homepage():
    best_data = load_best()
    return f"""
    <h1>Global Best Time</h1>
    <h2 id="time">{best_data['time'] if best_data['time'] != float('inf') else 'No record yet'} seconds</h2>
    <h3 id="name">{best_data['name']}</h3>
    <script>
    fetch('/best')
        .then(r => r.json())
        .then(data => {{
            const t = data.time;
            const n = data.name;
            document.getElementById("time").innerText =
                t !== Infinity ? t.toFixed(3) + " seconds" : "No record yet";
            document.getElementById("name").innerText = n;
        }});
    </script>
    """

if __name__ == "__main__":
    print("Starting server...")
    app.run(host="0.0.0.0", port=5000)