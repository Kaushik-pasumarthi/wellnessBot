from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            age_group TEXT,
            language TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    age_group = data.get("age_group")
    language = data.get("language")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (email, password, name, age_group, language) VALUES (?, ?, ?, ?, ?)",
            (email, hashed_password, name, age_group, language)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route("/profile", methods=["GET"])
def get_profile():
    email = request.args.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT name, age_group, language FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user:
        profile = {
            "name": user["name"] or "",
            "age_group": user["age_group"] or "18-25",
            "language": user["language"] or "English"
        }
        return jsonify({"success": True, "profile": profile})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

@app.route("/profile", methods=["POST"])
def profile():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    age_group = data.get("age_group")
    language = data.get("language")

    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET name=?, age_group=?, language=? WHERE email=?",
        (name, age_group, language, email)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Profile updated successfully"})

@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not email or not old_password or not new_password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user and check_password_hash(user["password"], old_password):
        hashed_new = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password=? WHERE email=?", (hashed_new, email))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Password updated successfully"})
    
    conn.close()
    return jsonify({"success": False, "message": "Invalid old password"}), 401

if __name__ == "__main__":
    app.run(debug=True)