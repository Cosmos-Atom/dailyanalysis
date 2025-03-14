from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            rating INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    rating = request.json.get("rating")
    date = datetime.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    
    # Check if a rating already exists for today
    c.execute("SELECT * FROM ratings WHERE date = ?", (date,))
    existing = c.fetchone()
    
    if existing:
        return jsonify({"error": "You can only submit one rating per day."}), 400
    
    c.execute("INSERT INTO ratings (date, rating) VALUES (?, ?)", (date, rating))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Rating submitted successfully!"})

@app.route("/data/daily")
def get_daily_data():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("SELECT date, rating FROM ratings ORDER BY date")
    data = c.fetchall()
    conn.close()

    return jsonify(data)

@app.route("/data/weekly")
def get_weekly_data():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y-%W', date) AS week, ROUND(AVG(rating), 2) 
        FROM ratings 
        GROUP BY week 
        ORDER BY week
    """)
    data = c.fetchall()
    conn.close()

    return jsonify(data)

@app.route("/data/monthly")
def get_monthly_data():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(rating), 2) 
        FROM ratings 
        GROUP BY month 
        ORDER BY month
    """)
    data = c.fetchall()
    conn.close()

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
