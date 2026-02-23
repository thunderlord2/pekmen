from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

# Get Render database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# Initialize table
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            time FLOAT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Get current best score
def get_best():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, time FROM scores ORDER BY time ASC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"name": row[0], "time": row[1]}
    return {"name": "", "time": float("inf")}

# Insert a new score
def insert_score(name, time_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO scores (name, time) VALUES (%s, %s)", (name, time_value))
    conn.commit()
    cur.close()
    conn.close()

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    new_time = data.get("time")
    name = data.get("name", "Unknown")

    if new_time is None:
        return jsonify({"error": "Missing time"}), 400

    best = get_best()

    if new_time < best["time"]:
        insert_score(name, new_time)
        return jsonify({"status": "new_record", "best": {"name": name, "time": new_time}})
    else:
        return jsonify({"status": "not_record", "best": best})

@app.route("/best", methods=["GET"])
def best():
    return jsonify(get_best())

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)