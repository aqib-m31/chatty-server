from flask import abort, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from flask_socketio import join_room, leave_room

from db_operations import *
from env_setup import *


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Server is running!"})


@app.route("/register", methods=["POST"])
def register():
    """
    Handles the 'register' route. It validates the input fields, checks the username and password constraints,
    inserts the user into the database, and returns a JSON response with an access token.

    :return: If an error occurs, returns a JSON response with an error message.
    """
    if request.method == "POST":
        data = validate_input(["username", "password", "confirm_password"])
        username = data["username"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        if len(username) < 4 or len(username) > 10:
            return jsonify(
                {
                    "error": True,
                    "message": "Username length should be between 4 to 10 characters.",
                }
            )

        if password != confirm_password:
            return jsonify({"error": True, "message": "Passwords must match."})

        if len(password) < 8:
            return jsonify(
                {"error": True, "message": "Password length must be greater than 8."}
            )

        if get_user(username) is not None:
            return jsonify({"error": True, "message": "Username already exists!"})

        try:
            insert_user(username, bcrypt.generate_password_hash(password))
            access_token = create_access_token(identity=username, expires_delta=False)
        except Exception as e:
            return jsonify({"error": True, "message": str(e)})

        return jsonify(
            {
                "error": False,
                "message": "Successfully registered",
                "username": username,
                "access_token": access_token,
            }
        )

    abort(405, description="Method not allowed.")


@app.route("/login", methods=["POST"])
def login():
    """
    Handles the 'login' route. It validates the input fields, checks the username and password,
    and returns a JSON response with an access token.

    :return: If an error occurs, returns a JSON response with an error message.
    """
    if request.method == "POST":
        data = validate_input(["username", "password"])
        username = data["username"]
        password = data["password"]

        user = get_user(username)
        if user is None:
            return jsonify({"error": True, "message": "Please check username!"})

        if not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"error": True, "message": "Check your password!"})

        access_token = create_access_token(identity=username, expires_delta=False)
        return jsonify(
            {
                "error": False,
                "message": "Successfully Logged In",
                "username": username,
                "access_token": access_token,
            }
        )

    abort(405, description="Method not allowed.")


@app.route("/rooms", methods=["POST"])
@jwt_required()
def get_rooms():
    """
    Handles the 'rooms' route. It extracts the username from the JWT token,
    retrieves all rooms associated with the user, and returns them in a JSON response.

    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        return jsonify(get_all_users_rooms(username))
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("delete")
@jwt_required()
def on_delete(data):
    """
    Handles the 'delete' event. It extracts the username and room ID from the JWT token and data respectively,
    checks if the room exists and belongs to the user, deletes the room, and emits a 'delete_response' event to the client.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        room_id = data["roomId"]
        room_info = get_room(room_id, username)
        if room_info == None:
            socketio.emit(
                "delete_response",
                {"error": True, "message": "FORBIDDEN!"},
                to=request.sid,
            )
        else:
            delete_room(room_id)
            socketio.emit(
                "delete_response",
                {
                    "error": False,
                    "message": f"{room_info['room_name']} deleted by owner [{username}]",
                },
            )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("create")
@jwt_required()
def on_create(data):
    """
    Handles the 'create' event. It extracts the username and room name from the JWT token and data respectively,
    creates a new room, makes the user join the room, and emits a 'create_response' and 'join_response' event to the client.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        room = data["room"]
        room_info = insert_room(room, username)
        if room_info is None:
            socketio.emit(
                "create_response",
                {"message": f"Room {room} already exists!"},
                to=request.sid,
            )
        else:
            room_id = str(room_info.inserted_id)
            join_room(room)
            socketio.emit(
                "create_response", {"message": f"Room {room} created!"}, to=request.sid
            )
            socketio.emit(
                "join_response",
                {
                    "message": f"{username} joined {room}!",
                    "roomId": room_id,
                    "roomName": room,
                },
                to=request.sid,
            )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("switch")
@jwt_required()
def on_switch(data):
    """
    Handles the 'switch' event. It extracts the username, the room to leave, and the room to join from the data,
    makes the user leave the first room and join the second room, and emits a 'switch_room_response' and 'join_response' event to the client.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        leave_room_id = data["leaveRoom"]
        join_room_id = data["joinRoom"]
        leave_room_name = get_room(leave_room_id)["room_name"]
        join_room_name = get_room(join_room_id)["room_name"]
        leave_room(leave_room_name)
        join_room(join_room_name)
        socketio.emit(
            "switch_room_response",
            {
                "message": f"{username} has left the room {leave_room_name} and joined the room {join_room_name}"
            },
            to=request.sid,
        )
        socketio.emit(
            "join_response",
            {
                "message": f"{username} joined {join_room_name}!",
                "roomId": join_room_id,
                "roomName": join_room_name,
            },
            to=request.sid,
        )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("temp_leave")
@jwt_required()
def on_temp_leave(data):
    """
    Handles the 'temp_leave' socket event. It allows a user to temporarily leave a room.

    :param data: A dictionary containing the ID of the room to leave under the key 'leaveRoom'.
    :return: Emits a 'temp_leave_room_response' event to the client with a message indicating that the user has left the room.
             If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        leave_room_id = data["roomId"]
        leave_room_name = get_room(leave_room_id)["room_name"]
        leave_room(leave_room_name)
        socketio.emit(
            "temp_leave_room_response",
            {"message": f"{username} has left the room {leave_room_name} temporarily."},
            to=request.sid,
        )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("join")
@jwt_required()
def on_join(data):
    """
    Handles the 'join' event. It extracts the username and room ID from the data,
    checks if the room exists, adds the user to the room, and emits a 'join_response' event to the client.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        room_id = data["roomId"]
        room_info = get_room(room_id)
        if room_info == None:
            socketio.emit(
                "join_response", {"message": "Room doesn't exist!"}, to=request.sid
            )
        else:
            room_name = room_info["room_name"]
            insert_user_in_room(room_id, username)
            join_room(room_name)
            socketio.emit(
                "join_response",
                {
                    "message": f"{username} joined {room_name}!",
                    "roomId": room_id,
                    "roomName": room_name,
                },
                to=request.sid,
            )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("leave")
@jwt_required()
def on_leave(data):
    """
    Handles the 'leave' event. It extracts the username and room ID from the data,
    checks if the room exists, removes the user from the room, and emits a 'leave_response'
    event to the client.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        username = get_jwt_identity()
        room_id = data["roomId"]
        room_info = get_room(room_id)
        if room_info == None:
            socketio.emit(
                "leave_response", {"message": "Room doesn't exist!"}, to=request.sid
            )
        else:
            room_name = room_info["room_name"]
            remove_user_from_room(room_id, username)
            leave_room(room_name)
            socketio.emit(
                "leave_response",
                {"message": f"{username} left {room_name}!"},
                to=request.sid,
            )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("message")
@jwt_required()
def handle_message(data):
    """
    Handles the 'message' event. It extracts the message, sender, and room from the data,
    and emits a 'message' event to all clients connected to the room.

    :param data: A dictionary that contains the data sent by the client.
    :return: If an error occurs, returns a JSON response with an error message and a 401 status code.
    """
    try:
        text = data["message"].strip()
        sender = get_jwt_identity()
        room = data["room"]
        socketio.emit(
            "message", {"message": text, "sender": sender, "room": room}, to=room
        )
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 401


@socketio.on("connect")
def on_connect():
    """
    Handles the 'connect' event. It prints a message that includes the session ID of the connected client.
    """
    print("Client connected: " + request.sid)


@socketio.on("disconnect")
def on_disconnect():
    """
    Handles the 'disconnect' event. It prints a message that includes the session ID of the disconnected client.
    """
    print("Client disconnected: " + request.sid)


def validate_input(fields):
    """
    Validates the input fields in the request form. If a field is missing or empty, it aborts the request with a 400 status code.

    :param fields: A list of field names to validate.
    :return: The request form if all fields are valid.
    """
    for field in fields:
        if field not in request.form:
            abort(400, description=f"Bad Request: Missing {field}.")
        if len(request.form[field]) == 0:
            abort(400, description=f"Bad Request: Empty {field}.")
    return request.form


def get_all_users_rooms(username):
    """
    Retrieves all rooms associated with a user. The rooms are categorized into 'own' and 'others' based on the creator of the room.

    :param username: The username of the user.
    :return: A dictionary containing the rooms categorized into 'own' and 'others'.
    """
    rooms = {"own": [], "others": []}
    for room in get_user_rooms(username):
        room_info = {"id": str(room.get("_id")), "name": room.get("room_name")}
        if room.get("creator") == username:
            rooms["own"].append(room_info)
        else:
            rooms["others"].append(room_info)
    return rooms


# Run the app
if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5500)
