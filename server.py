from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BEST_FILE = "global_best.txt"

# Create file if it doesn't exist
def init_file():
    if not os.path.exists(BEST_FILE):
        with open(BEST_FILE, "w") as f:
            f.write("None\n")
            f.write("999999999\n")

init_file()

# Read best score
def get_best():
    try:
        with open(BEST_FILE, "r") as f:
            lines = f.readlines()

            if len(lines) < 2:
                return {"name": "", "time": None}

            name = lines[0].strip()
            time_value = float(lines[1].strip())

            if name == "None":
                return {"name": "", "time": None}

            return {
                "name": name,
                "time": time_value
            }

    except:
        return {"name": "", "time": None}

# Save new best score
def save_best(name, time_value):
    with open(BEST_FILE, "w") as f:
        f.write(f"{name}\n")
        f.write(f"{time_value}\n")

@app.route("/")
def homepage():
    return """
<!DOCTYPE html>
<head>
    <style>
        body {
            background-color: #020403;
        }
        .text {
            color: azure;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="text" id="text1">
        <h1>Global Best Time</h1>
        <h2 id="time">Loading...</h2>
        <h3 id="name"></h3>
    </div>
</body>
<footer>
        <script>
    fetch('/best')
        .then(r => r.json())
        .then(data => {

            if (data.time === null) {
                document.getElementById("time").innerText =
                    "No record yet";

                return;
            }

            document.getElementById("time").innerText =
                data.time.toFixed(3) + " seconds";

            document.getElementById("name").innerText =
                "By: " + data.name;
        });
    </script>
</footer>
    """

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    new_time = data.get("time")
    name = data.get("name", "Unknown")

    if new_time is None:
        return jsonify({"error": "Missing time"}), 400

    best = get_best()

    # If no record yet OR better time
    if best["time"] is None or new_time < best["time"]:

        save_best(name, new_time)

        return jsonify({
            "status": "new_record",
            "best": {
                "name": name,
                "time": new_time
            }
        })

    return jsonify({
        "status": "not_record",
        "best": best
    })

@app.route("/best")
def best():
    return jsonify(get_best())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )