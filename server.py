from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BEST_TIME_FILE = "global_best.txt"

# Load best time
def load_best():
    if not os.path.exists(BEST_TIME_FILE):
        return float("inf")
    with open(BEST_TIME_FILE, "r") as f:
        try:
            return float(f.read().strip())
        except:
            return float("inf")

# Save best time
def save_best(time_value):
    with open(BEST_TIME_FILE, "w") as f:
        f.write(f"{time_value:.3f}")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    new_time = data.get("time")

    if new_time is None:
        return jsonify({"error": "Missing time"}), 400

    current_best = load_best()

    if new_time < current_best:
        save_best(new_time)
        return jsonify({"status": "new_record", "best": new_time})
    else:
        return jsonify({"status": "not_record", "best": current_best})

@app.route("/best", methods=["GET"])
def best():
    return jsonify({"best": load_best()})

@app.route("/")
def homepage():
    return """
    <h1>Global Best Time</h1>
    <h2 id="time">Loading...</h2>
    <script>
    fetch('/best')
        .then(r => r.json())
        .then(data => {
            document.getElementById("time").innerText =
                data.best.toFixed(3) + " seconds";
        });
    </script>
    """

if __name__ == "__main__":
    print("Starting server...")
    app.run(host="127.0.0.1", port=5000, debug=True)