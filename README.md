# chatty-server
Chatty Server is the chat server designed to complement the Chatty App. Built with Flask, Flask-SocketIO, and MongoDB, it facilitates real-time messaging and seamless interactions within chat rooms.

## Features
- **User Registration and Login**: Securely register and log in to access personalized chat experiences.

- **JWT Authentication**: Implementing JSON Web Token (JWT) authentication for enhanced security.

- **Real-time Messaging**: Engage in dynamic conversations with instant messaging capabilities.

- **Room Creation and Joining**: Create new chat rooms and join existing ones using unique IDs.

- **Room Switching**: Seamlessly switch between different chat rooms.

## Getting Started
To run the [Chatty App](https://github.com/aqib-m31/Chatty), start by running this Chatty Server:
- Clone the chatty-server repository to your local machine.
- Create a virtual environment for the server using your preferred method.
- Install the required packages using pip.
    `pip install -r requirements.txt`
- Set up Environment Variables:
    - Create a `.env` file in the root of the Chatty Server and populate it with the following variables:
        - `APP_SECRET_KEY`: Secret key for securing Flask application data.
        - `JWT_SECRET_KEY`: Key for signing and verifying JSON Web Tokens (JWT).
        - `CONNECTION_STRING`: MongoDB database connection string.
        - `JWT_IDENTITY_CLAIM`: Identity claim for JWT subject.
        - `DB_NAME`: Name of the MongoDB database.

- Run the Server:
    `python app.py`

Voila! Your Chatty Server is up and running. Now you can proceed to run the [Chatty App](https://github.com/aqib-m31/Chatty) and experience real-time connections in your chat rooms.