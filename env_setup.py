import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from pymongo import MongoClient

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

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
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    client = MongoClient(CONNECTION_STRING)
    return client[os.getenv("DB_NAME")]
