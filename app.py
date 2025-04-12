from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/testDB"
mongo = PyMongo(app)

def insert_hardcoded_data():
    """
    Inserts a hardcoded document into the 'users' collection.
    """
    try:
        # Insert a document directly
        user_id = mongo.db.users.insert_one({'name': 'Test User', 'age': 99}).inserted_id
        print(f"Inserted user with ID: {user_id}")  # Print to the console

    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/')
def hello():
    insert_hardcoded_data()  # Call the function when the root route is accessed.
    return "Data inserted! Check your MongoDB database."

if __name__ == '__main__':
    app.run(debug=True)
