from flask import Flask, send_from_directory
from flask_pymongo import PyMongo
import os
import time

# Create the Flask application
app = Flask(
    __name__,
    static_folder='frontend/build',  # Path to React build folder inside container
    static_url_path='/'
)

# Read environment variables for MongoDB configuration
mongo_host = os.environ.get('DATABASE_HOST', 'db')
mongo_port = int(os.environ.get('DATABASE_PORT', 27017))
mongo_db_name = os.environ.get('DATABASE_NAME', 'CSE312-SobEmoji')

# Construct the MongoDB URI without authentication
app.config["MONGO_URI"] = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"

# Initialize PyMongo with a retry mechanism
max_retries = 5
retry_delay = 5  # seconds
mongo = None  # Initialize mongo outside the loop
for i in range(max_retries):
    try:
        mongo = PyMongo(app)
        # Trigger a simple database command to check connection
        mongo.db.command('ping')
        print("Successfully connected to MongoDB.")
        break  # Exit the loop if connection is successful
    except Exception as e:
        print(f"Attempt {i+1} to connect to MongoDB failed: {e}")
        if i < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise  # Re-raise the exception if all retries fail

@app.route('/api/insert')
def insert_hardcoded_data():
    """
    Inserts a hardcoded document into the 'users' collection.
    """
    try:
        if mongo:  # Check if mongo client is initialized
            user_id = mongo.db.users.insert_one({'name': 'Test User', 'age': 99}).inserted_id
            print(f"Inserted user with ID: {user_id}")
            return {"status": "success", "inserted_id": str(user_id)}
        else:
            print("MongoDB client not initialized. Cannot insert data.")
            return {"status": "error", "message": "MongoDB client not initialized"}
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")
        return {"status": "error", "message": str(e)}

# Serve the main React index.html
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (CSS, JS, etc.) or fallback to index.html for React Router
@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
