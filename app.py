from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
import os
import time
import bcrypt
import re
import logging
from datetime import datetime

app = Flask(
    __name__,
    static_folder='frontend/build',
    static_url_path='/'
)

# MongoDB Configuration
mongo_host = os.environ.get('DATABASE_HOST', 'db')
mongo_port = int(os.environ.get('DATABASE_PORT', 27017))
mongo_db_name = os.environ.get('DATABASE_NAME', 'CSE312-SobEmoji')
app.config["MONGO_URI"] = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"

# MongoDB Connection with Retry
max_retries = 5
retry_delay = 5
mongo = None
for i in range(max_retries):
    try:
        mongo = PyMongo(app)
        mongo.db.command('ping')
        print("Successfully connected to MongoDB.")
        break
    except Exception as e:
        print(f"Attempt {i+1} to connect to MongoDB failed: {e}")
        if i < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise

# Setup Logging
if not os.path.exists('/logs'):
    os.makedirs('/logs')

log_formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file_handler = logging.FileHandler('/logs/server.log')
log_file_handler.setFormatter(log_formatter)
log_file_handler.setLevel(logging.INFO)

app.logger.addHandler(log_file_handler)
app.logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    ip = request.remote_addr
    method = request.method
    path = request.path
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    app.logger.info(f"{timestamp} - {ip} - {method} {path}")

# Helpers
def is_valid_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[^A-Za-z0-9]', password) is not None
    )

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    if not is_valid_password(password):
        return jsonify({
            "status": "error",
            "message": "Password must be at least 8 characters and include a special character"
        }), 400

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"status": "error", "message": "Username already exists"}), 409

    hashed_pw = hash_password(password)
    mongo.db.users.insert_one({"username": username, "password": hashed_pw})
    return jsonify({"status": "success", "message": "User registered"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = mongo.db.users.find_one({"username": username})
    if not user or not check_password(password, user["password"]):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    return jsonify({"status": "success", "message": "Login successful"}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    data = request.get_json() or {}
    username = data.get('username', 'unknown')
    app.logger.info(f"User '{username}' logged out.")
    return jsonify({"status": "success", "message": "Logged out"}), 200

@app.route('/api/insert')
def insert_hardcoded_data():
    try:
        if mongo:
            user_id = mongo.db.users.insert_one({'name': 'Test User', 'age': 99}).inserted_id
            app.logger.info(f"Inserted user with ID: {user_id}")
            return {"status": "success", "inserted_id": str(user_id)}
        else:
            app.logger.error("MongoDB client not initialized. Cannot insert data.")
            return {"status": "error", "message": "MongoDB client not initialized"}
    except Exception as e:
        app.logger.error(f"An error occurred during data insertion: {e}")
        return {"status": "error", "message": str(e)}

# Serve React Frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
