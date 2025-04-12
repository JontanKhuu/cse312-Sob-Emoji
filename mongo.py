from flask_pymongo import PyMongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()

def init_mongo(app):
    """Initialize the MongoDB connection using Flask-PyMongo."""
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mydatabase")
    mongo.init_app(app)
    return mongo
