from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from env_setup import get_database

dbname = get_database()
users_collection = dbname["users"]
rooms_collection = dbname["rooms"]
rooms_collection.create_index("room_name", unique=True)
users_collection.create_index("username", unique=True)


def insert_user(username, password):
    """
    Handles the 'login' route. It validates the input fields, checks the username and password,
    and returns a JSON response with an access token.

    :return: If an error occurs, returns a JSON response with an error message.
    """
    try:
        users_collection.insert_one(
            {
                "username": username,
                "password": password,
            }
        )
    except DuplicateKeyError:
        return None


def get_user_rooms(username):
    """
    Handles the 'login' route. It validates the input fields, checks the username and password,
    and returns a JSON response with an access token.

    :return: If an error occurs, returns a JSON response with an error message.
    """
    return rooms_collection.find({"$or": [{"creator": username}, {"users": username}]})


def get_room(room_id, username=None):
    """
    Retrieves a room by its ID. If a username is provided, it also checks that the user is the creator of the room.

    :param room_id: The ID of the room.
    :param username: The username of the user (optional).
    :return: The room document, or None if no such room exists.
    """
    if username is not None:
        return rooms_collection.find_one(
            {"_id": ObjectId(room_id), "creator": username}
        )
    return rooms_collection.find_one({"_id": ObjectId(room_id)})


def delete_room(room_id):
    """
    Deletes a room by its ID.

    :param room_id: The ID of the room.
    :return: The result of the delete operation.
    """
    return rooms_collection.delete_one({"_id": ObjectId(room_id)})


def get_user(username):
    """
    Retrieves a user by their username.

    :param username: The username of the user.
    :return: The user document, or None if no such user exists.
    """
    return users_collection.find_one({"username": username})


def insert_room(room_name, username):
    """
    Inserts a new room into the rooms collection.

    :param room_name: The name of the room.
    :param username: The username of the user who is creating the room.
    :return: The result of the insert operation, or None if a room with the same name already exists.
    """
    try:
        return rooms_collection.insert_one(
            {"room_name": room_name, "users": [username], "creator": username}
        )
    except DuplicateKeyError:
        return None


def insert_user_in_room(room_id, username):
    """
    Adds a user to a room.

    :param room_id: The ID of the room.
    :param username: The username of the user.
    :return: The result of the update operation.
    """
    return rooms_collection.update_one(
        {"_id": ObjectId(room_id)}, {"$addToSet": {"users": username}}
    )


def remove_user_from_room(room_id, username):
    """
    Removes a user from a room.

    :param room_id: The ID of the room.
    :param username: The username of the user.
    :return: The result of the update operation.
    """
    return rooms_collection.update_one(
        {"_id": ObjectId(room_id)}, {"$pull": {"users": username}}
    )
