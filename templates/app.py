from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Initialize database
def init_db():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    
    # Create users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    
    # Create ratings table with username
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            rating INTEGER,
            UNIQUE(username, date)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    
    # Get the list of all users except the current one for the switch option
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username != ?", (session["username"],))
    other_users = [user[0] for user in c.fetchall()]
    conn.close()
    
    # Get the currently viewed user (default to logged-in user)
    view_user = session.get("view_user", session["username"])
    view_only = view_user != session["username"]
    
    return render_template("index.html", 
                          username=session["username"], 
                          view_user=view_user,
                          other_users=other_users,
                          view_only=view_only)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("ratings.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session["username"] = username
            session["view_user"] = username  # Initially view your own data
            return redirect(url_for("index"))
        else:
            return "Invalid credentials!", 401
    
    return render_template("login.html")

@app.route("/switch_user/<username>")
def switch_user(username):
    if "username" not in session:
        return redirect(url_for("login"))
    
    # Verify the requested user exists
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        session["view_user"] = username
        return redirect(url_for("index"))
    else:
        return "User not found", 404

@app.route("/reset_view")
def reset_view():
    if "username" in session:
        session["view_user"] = session["username"]
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("view_user", None)
    return redirect(url_for("login"))

@app.route("/submit", methods=["POST"])
def submit():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Only allow rating submission for your own account
    if session.get("view_user") != session["username"]:
        return jsonify({"error": "You can only submit ratings for your own account"}), 403
    
    rating = request.json.get("rating")
    date = datetime.today().strftime('%Y-%m-%d')
    username = session["username"]
    
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ratings WHERE username = ? AND date = ?", (username, date))
    existing = c.fetchone()
    
    if existing:
        return jsonify({"error": "You can only submit one rating per day."}), 400
    
    c.execute("INSERT INTO ratings (username, date, rating) VALUES (?, ?, ?)", (username, date, rating))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Rating submitted successfully!"})

@app.route("/data/<chart_type>")
def get_data(chart_type):
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Use the view_user parameter to get data for either current user or the user we're viewing
    view_user = session.get("view_user", session["username"])
    
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()
    
    if chart_type == "daily":
        c.execute("SELECT date, rating FROM ratings WHERE username = ? ORDER BY date", (view_user,))
    elif chart_type == "weekly":
        c.execute("""
            SELECT strftime('%Y-%W', date) AS week, ROUND(AVG(rating), 2) 
            FROM ratings 
            WHERE username = ?
            GROUP BY week 
            ORDER BY week
        """, (view_user,))
    elif chart_type == "monthly":
        c.execute("""
            SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(rating), 2) 
            FROM ratings 
            WHERE username = ?
            GROUP BY month 
            ORDER BY month
        """, (view_user,))
    else:
        return jsonify({"error": "Invalid chart type"}), 400
    
    data = c.fetchall()
    conn.close()
    
    return jsonify(data)


import sqlite3

def add_users():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()

    users = [
        ("cosmos_atom", "Danvers"),
        ("yasasree_lasya", "Alison")
    ]

    for username, password in users:
        c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()
    print("Users added successfully!")

if __name__ == "__main__":
    add_users()  # Add predefined users before running the app
    app.run(debug=True)  # Start Flask app