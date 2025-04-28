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

# --- Flask Setup ---
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
socketio = SocketIO(app, cors_allowed_origins="*")

# --- MongoDB Setup ---
mongo_host = os.environ.get('DATABASE_HOST', 'db')
mongo_port = int(os.environ.get('DATABASE_PORT', 27017))
mongo_db_name = os.environ.get('DATABASE_NAME', 'CSE312-SobEmoji')
app.config["MONGO_URI"] = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"
if not os.path.exists('/logs'):
    os.makedirs('/logs', exist_ok=True)

log_formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file_handler = logging.FileHandler('/logs/server.log')
log_file_handler.setFormatter(log_formatter)
log_file_handler.setLevel(logging.INFO)


app.logger.setLevel(logging.INFO)
app.logger.addHandler(log_file_handler)
# Log every request
@app.before_request
def log_request_info():
    ip = request.remote_addr
    method = request.method
    path = request.path
    app.logger.info(f"{ip} - {method} {path}")
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

# --- Game State ---
players = {}   # { sid : { username, x, y, score } }
foods = []     # [{x, y}]
game_running = False

def spawn_food():
    return {'x': random.randint(0, 19), 'y': random.randint(0, 19)}

# --- WebSocket Handlers ---
@socketio.on('join_game')
def join_game(data):
    username = data.get('username')
    if username:
        sid = request.sid
        players[sid] = {
            'username': username,
            'x': random.randint(0, 19),
            'y': random.randint(0, 19),
            'score': 0
        }
        print(f"✅ {username} joined the game!")
        emit('players_update', {'players': list(players.values())}, broadcast=True)
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
        if time.time() - start_time >= 60:
            end_game()
@socketio.on('force_end_game')
def end_game():
    global game_running
    print("🏁 Game ending")
    game_running = False

    if players:
        winner = max(players.values(), key=lambda p: p['score'])
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

# Start game loop on server start
@socketio.on('start_game')
def start_game():
    if not game_running:
        socketio.start_background_task(game_loop)

# --- REST APIs ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    if not is_valid_password(password):
        return jsonify({"status": "error", "message": "Password must be at least 8 characters and include a special character"}), 400
    if mongo.db.users.find_one({"username": username}):
        return jsonify({"status": "error", "message": "Username already exists"}), 409
    mongo.db.users.insert_one({"username": username, "password": hash_password(password)})
    return jsonify({"status": "success", "message": "Registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = mongo.db.users.find_one({"username": username})
    if user and check_password(password, user['password']):
        return jsonify({"status": "success", "message": "Login successful", "token": "dummy-token"}), 200
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

# --- Static Serving ---
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# --- Start ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
