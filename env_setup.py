import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

CORS(app, resources={
    r"/register": {"origins": "*"},
    r"/login": {"origins": "*"},
    r"/rooms": {"origins": "*"},
    r"/socket.io/*": {"origins": "*"}
})

socketio = SocketIO(app, cors_allowed_origins="*")

# Set the secret key for the Flask application. This is necessary for session security.
app.secret_key = os.getenv("APP_SECRET_KEY")

# Initialize JWTManager with the Flask app
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_IDENTITY_CLAIM"] = os.getenv("JWT_IDENTITY_CLAIM")

# Initialize SocketIO with the Flask app
socketio = SocketIO(app)

# Initialize Bcrypt with the Flask app
bcrypt = Bcrypt(app)



def get_database():
    try:
        CONNECTION_STRING = os.getenv("CONNECTION_STRING")
        client = MongoClient(CONNECTION_STRING)
        db = client[os.getenv("DB_NAME")]
        # Attempt to retrieve a collection to ensure connection is established
        db.list_collection_names()
        return db
    except ServerSelectionTimeoutError:
        print("Failed to connect to the database. Please check your connection string and network connectivity.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
