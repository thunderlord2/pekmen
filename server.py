from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = "leaderboard.db"

# =========================
# DATABASE SETUP
# =========================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_best():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, time FROM scores ORDER BY time ASC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        return {"name": row[0], "time": row[1]}
    return {"name": "", "time": float("inf")}

def insert_score(name, time_value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO scores (name, time) VALUES (?, ?)", (name, time_value))
    conn.commit()
    conn.close()

# Initialize database when server starts
init_db()

# =========================
# SUBMIT ENDPOINT
# =========================

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    new_time = data.get("time")
    name = data.get("name", "Unknown")

    if new_time is None:
        return jsonify({"error": "Missing time"}), 400

    current_best = get_best()

    if new_time < current_best["time"]:
        insert_score(name, new_time)
        return jsonify({"status": "new_record", "best": {"name": name, "time": new_time}})
    else:
        return jsonify({"status": "not_record", "best": current_best})

# =========================
# BEST ENDPOINT
# =========================

@app.route("/best")
def best():
    return jsonify(get_best())

# =========================
# HOMEPAGE
# =========================

@app.route("/")
def homepage():
    return """
    <h1>🏆 Global Best Time</h1>
    <h2 id="time">Loading...</h2>
    <h3 id="name"></h3>
    <script>
    fetch('/best')
        .then(r => r.json())
        .then(data => {
            if (data.time === Infinity) {
                document.getElementById("time").innerText = "No record yet";
                document.getElementById("name").innerText = "";
            } else {
                document.getElementById("time").innerText = data.time.toFixed(3) + " seconds";
                document.getElementById("name").innerText = "👑 " + data.name;
            }
        });
    </script>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)