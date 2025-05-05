# app.py

import os
import time
import bcrypt
import re
import eventlet
eventlet.monkey_patch()
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, emit
from datetime import datetime
import random
import logging
from werkzeug.utils import secure_filename
from PIL import Image
from flask import g
# --- Flask Setup ---
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
socketio = SocketIO(app, cors_allowed_origins="*")

# --- MongoDB Setup ---
mongo_host = os.environ.get('DATABASE_HOST', 'db')
mongo_port = int(os.environ.get('DATABASE_PORT', 27017))
mongo_db_name = os.environ.get('DATABASE_NAME', 'CSE312-SobEmoji')
app.config["MONGO_URI"] = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"
if not os.path.exists('/logs'):
    os.makedirs('./logs', exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(),'avatars')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Server log: for readable logs like requests and response codes
log_formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file_handler = logging.FileHandler('/logs/server.log')
log_file_handler.setFormatter(log_formatter)
log_file_handler.setLevel(logging.INFO)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(log_file_handler)  # ✅ This stays

# Raw HTTP log: separate logger for raw HTTP request/response
raw_log_handler = logging.FileHandler('/logs/raw_http.log')
raw_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
raw_log_handler.setLevel(logging.INFO)

raw_logger = logging.getLogger('raw_logger')
raw_logger.setLevel(logging.INFO)
raw_logger.addHandler(raw_log_handler)  # ✅ Only added to raw_logger


@app.before_request
def combined_before_request():
    # === 1. RAW HTTP LOGGING ===
    try:
        headers = dict(request.headers)
        headers.pop("Authorization", None)
        log_entry = f"🟢 RAW REQUEST: {request.method} {request.path}\nHeaders: {headers}"

        body_data = request.get_data(as_text=True)

        if body_data and all(32 <= ord(c) <= 126 or c in '\r\n\t' for c in body_data[:256]):
            # Redact sensitive fields if JSON
            if request.content_type and 'application/json' in request.content_type:
                try:
                    import json
                    json_body = json.loads(body_data)
                    for key in list(json_body.keys()):
                        if 'password' in key.lower() or 'token' in key.lower():
                            json_body[key] = '[REDACTED]'
                    redacted_body = json.dumps(json_body)[:2048]
                    log_entry += f"\nBody (sanitized): {redacted_body}"
                except Exception:
                    log_entry += f"\nBody (raw): {body_data[:2048]}"
            else:
                log_entry += f"\nBody (non-JSON): {body_data[:2048]}"
        else:
            log_entry += "\n[Binary or non-text body skipped]"

        raw_logger.info(log_entry)
    except Exception as e:
        app.logger.error(f"Failed to log raw request: {e}")

    # === 2. SERVER.LOG LOGGING ===
    g.start_time = time.time()
    ip = request.remote_addr
    method = request.method
    path = request.path
    user = request.headers.get('Username', 'Anonymous')
    app.logger.info(f"REQUEST from {ip} ({user}) - {method} {path}")

    if request.method in ['POST', 'PUT']:
        headers = {k: v for k, v in request.headers.items() if 'auth' not in k.lower()}
        app.logger.info(f"HEADERS: {headers}")

        if request.content_type and 'application/json' in request.content_type:
            try:
                import json
                json_body = json.loads(request.get_data(as_text=True))
                for key in list(json_body.keys()):
                    if 'password' in key.lower() or 'token' in key.lower():
                        json_body[key] = '[REDACTED]'
                redacted_body = json.dumps(json_body)[:2048]
                app.logger.info(f"BODY: {redacted_body}")
            except Exception:
                body = request.get_data(as_text=True)[:2048]
                app.logger.info(f"BODY: {body}")

@app.after_request
def log_response_info(response):
    try:
        ip = request.remote_addr
        user = request.headers.get('Username', 'Anonymous')
        method = request.method
        path = request.path
        code = response.status_code
        app.logger.info(f"RESPONSE to {ip} ({user}) - {method} {path} - {code}")

        # Only log POST/PUT body content (optional and size-limited)
        if request.method in ['POST', 'PUT']:
            content_type = response.content_type or ''
            headers = {k: v for k, v in response.headers.items() if 'auth' not in k.lower()}
            app.logger.info(f"RESPONSE HEADERS: {headers}")

            if 'application/json' in content_type:
                try:
                    import json
                    response_data = json.loads(response.get_data(as_text=True))
                    for key in list(response_data.keys()):
                        if 'password' in key.lower() or 'token' in key.lower():
                            response_data[key] = '[REDACTED]'
                    sanitized = json.dumps(response_data)[:2048]
                    app.logger.info(f"RESPONSE BODY: {sanitized}")
                except Exception:
                    raw_body = response.get_data(as_text=True)[:2048]
                    app.logger.info(f"RESPONSE BODY (raw): {raw_body}")
            else:
                raw_body = response.get_data(as_text=True)[:2048]
                app.logger.info(f"RESPONSE BODY (non-JSON): {raw_body}")
    except Exception as e:
        app.logger.error(f"Failed to log response: {e}")

    return response
mongo = None
for i in range(5):
    try:
        mongo = PyMongo(app)
        mongo.db.command('ping')
        print("✅ Successfully connected to MongoDB.")
        break
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        time.sleep(5)

# --- Helper Functions ---
def is_valid_password(password):
    return len(password) >= 8 and re.search(r'[^A-Za-z0-9]', password)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def check_and_update_achievements(username):
    achievements = mongo.db.achievements.find_one({"username": username})
    if not achievements:
        # Initialize
        achievements = {
            "username": username,
            "played_1_game": False,
            "won_1_game": False,
            "ate_50_food": False
        }
        mongo.db.achievements.insert_one(achievements)

    stats = mongo.db.game_stats.find_one({"username": username}) or {}

    updates = {}
    if not achievements.get("played_1_game") and stats.get("games_played", 0) >= 1:
        updates["played_1_game"] = True
    if not achievements.get("won_1_game") and stats.get("games_won", 0) >= 1:
        updates["won_1_game"] = True
    if not achievements.get("ate_50_food") and stats.get("food_eaten", 0) >= 50:
        updates["ate_50_food"] = True

    if updates:
        mongo.db.achievements.update_one(
            {"username": username},
            {"$set": updates}
        )


# --- Game State ---
players = {}   # { sid : { username, x, y, score } }
foods = []     # [{x, y}]
game_running = False

def spawn_food():
    return {'x': random.randint(0, 19), 'y': random.randint(0, 19)}

@app.route('/api/achievements/<username>', methods=['GET'])
def get_user_achievements(username):
    achievements = mongo.db.achievements.find_one({"username": username}, {'_id': 0})
    if not achievements:
        achievements = {
            "played_1_game": False,
            "won_1_game": False,
            "ate_50_food": False
        }
    return jsonify(achievements)

# --- WebSocket Handlers ---
@socketio.on('join_game')
def join_game(data):
    username = data.get('username')
    if username:
        sid = request.sid

        # Fetch avatar from DB before assigning player
        user = mongo.db.users.find_one({"username": username})
        avatar_filename = user.get('avatar', 'default.png')

        players[sid] = {
            'username': username,
            'x': random.randint(0, 19),
            'y': random.randint(0, 19),
            'score': 0,
            'avatar': avatar_filename
        }
    
        # Increment games_played
        mongo.db.game_stats.update_one(
            {"username": username},
            {"$inc": {"games_played": 1}},
            {"$setOnInsert": {"games_played": 0, "games_won": 0, "food_eaten": 0}},
            upsert=True  # creates doc if it doesn't exist
        )
    

        print(f"✅ {username} joined the game!")
        emit('players_update', {'players': list(players.values())}, broadcast=True)

        socketio.emit('game_update', {
            'players': list(players.values()),
            'foods': foods
        })

@socketio.on('move')
def move(data):
    sid = request.sid
    direction = data.get('direction')
    player = players.get(sid)

    if player:
        # Calculate the intended new position
        new_x, new_y = player['x'], player['y']

        if direction == 'up':
            new_y = max(0, new_y - 1)
        elif direction == 'down':
            new_y = min(19, new_y + 1)
        elif direction == 'left':
            new_x = max(0, new_x - 1)
        elif direction == 'right':
            new_x = min(19, new_x + 1)

        # Check if the new position is occupied by another player
        collision = any(p['x'] == new_x and p['y'] == new_y for sid2, p in players.items() if sid2 != sid)

        if not collision:
            # Only update position if no collision
            player['x'] = new_x
            player['y'] = new_y

            # Check if player eats a food
            for food in foods:
                if player['x'] == food['x'] and player['y'] == food['y']:
                    player['score'] += 1
                    foods.remove(food)
                    foods.append(spawn_food())

                    # Increment food eaten count in MongoDB
                    mongo.db.game_stats.update_one(
                        {"username": player['username']},
                        {"$inc": {"food_eaten": 1}},
                        upsert=True
                    )
                    check_and_update_achievements(player['username'])
                    break
@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    if sid in players:
        username = players[sid]['username']
        print(f"⚡ {username} disconnected")
        del players[sid]
        emit('players_update', {'players': list(players.values())}, broadcast=True)

# --- Game Loop ---
def game_loop():
    global game_running
    game_running = True
    print("🚀 Game loop started")

    # Spawn initial food
    for _ in range(5):
        foods.append(spawn_food())

    start_time = time.time()

    while game_running:
        socketio.sleep(0.1)

        # Broadcast current game state
        socketio.emit('game_update', {
            'players': list(players.values()),
            'foods': foods
        })

        # End game after 2 minutes
        if time.time() - start_time >= 10:
            end_game()
@socketio.on('force_end_game')
def end_game():
    global game_running
    print("🏁 Game ending")
    game_running = False
    for player in players.values():
        mongo.db.game_stats.update_one(
            {"username": player['username']},
            {"$inc": {"games_played": 1}}
        )
        check_and_update_achievements(player['username'])
    
    if players:
        winner = max(players.values(), key=lambda p: p['score'])
        mongo.db.game_stats.update_one(
            {"username": winner['username']},
            {"$inc": {"games_won": 1}},
            upsert=True
        )
        check_and_update_achievements(winner['username'])
        socketio.emit('game_over', {
            'winner': winner['username'],
            'score': winner['score']
        })
    else:
        socketio.emit('game_over', {
            'winner': None,
            'score': 0
        })
    
    players.clear()
    foods.clear()
@socketio.on('start_game')
def start_game():
    if not game_running:
        socketio.start_background_task(game_loop)
@app.route('/api/stats/<username>', methods=['GET'])
def get_user_stats(username):
    user_stats = mongo.db.game_stats.find_one({"username": username})
    if not user_stats:
        return jsonify({"games_played": 0, "games_won": 0})
    return jsonify({
        "games_played": user_stats.get("games_played", 0),
        "games_won": user_stats.get("games_won", 0)
    })

# --- REST APIs ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        app.logger.info(f"Register success: {username}")  # on success
        app.logger.info(f"Register failed: {username} - reason: <reason>")

        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    if not is_valid_password(password):
        app.logger.info(f"Register success: {username}")  # on success
        app.logger.info(f"Register failed: {username} - reason: <reason>")

        return jsonify({"status": "error", "message": "Password must be at least 8 characters and include a special character"}), 400
    if mongo.db.users.find_one({"username": username}):
        app.logger.info(f"Register success: {username}")  # on success
        app.logger.info(f"Register failed: {username} - reason: <reason>")

        return jsonify({"status": "error", "message": "Username already exists"}), 409
    mongo.db.users.insert_one({"username": username, "password": hash_password(password)})
    app.logger.info(f"Register success: {username}")  # on success
    app.logger.info(f"Register failed: {username} - reason: <reason>")

    return jsonify({"status": "success", "message": "Registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = mongo.db.users.find_one({"username": username})
    
    
    if user and check_password(password, user['password']):
        app.logger.info(f"Login success: {username}")  # on success
        return jsonify({"status": "success", "message": "Login successful", "token": "dummy-token"}), 200
    app.logger.info(f"Login failed: {username} - Invalid credentials")

    return jsonify({"status": "error", "message": "Invalid username or password"}), 401
@app.route('/api/upload-avatar', methods=['POST'])
def upload_avatar():
    print("🟡 Reached upload-avatar endpoint")
    if 'avatar' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files['avatar']
    username = request.form.get('username')

    if not username or not file.filename or not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Missing or invalid file/username"}), 400

    try:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{username}.{ext}")
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        img = Image.open(file.stream)
        img.save(avatar_path)

        # 🔄 Update user in MongoDB to store the avatar filename
        mongo.db.users.update_one(
            {"username": username},
            {"$set": {"avatar": filename}}
        )

        return jsonify({"status": "success", "message": "Avatar uploaded"}), 200
    except Exception as e:
        print("Avatar upload error:", e)
        return jsonify({"status": "error", "message": "Invalid image"}), 400

@app.route('/api/game-stats', methods=['GET'])
def get_all_game_stats():
    stats = list(mongo.db.game_stats.find({}, {'_id': 0}))  # Exclude Mongo's default `_id` field
    return jsonify(stats)

# --- Static Serving ---
@app.route('/avatars/<filename>')
def get_avatar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)
@app.route('/api/clear-game-data', methods=['POST'])
def clear_game_data():
    mongo.db.game_stats.drop()
    mongo.db.food_stats.drop()
    mongo.db.achievements.drop()
    return jsonify({"status": "success", "message": "Game-related collections cleared."})
if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=8080)
    except Exception as e:
        import traceback
        app.logger.error("Unhandled exception:\n" + traceback.format_exc())

