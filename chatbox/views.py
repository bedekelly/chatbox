from werkzeug.exceptions import BadRequest
from . import app
from flask import request, jsonify
from .messages import message_queue


@app.route("/")
def index():
    """The main page of the application."""
    return app.send_static_file("index.html")


@app.route("/messages", methods=["POST"])
def add_message():
    """
    Post a message to the chatroom, by adding it to our message queue.
    """
    try:
        message_data = request.get_json()
    except BadRequest:
        # The JSON was malformed in some way.
        try:
            # The request was valid UTF-8 encoded text.
            original_text = request.data.decode("utf-8")
        except UnicodeDecodeError as e:
            # The request was something other than UTF-8.
            original_text = ("Original text not available. Server encountered"
                             " an error while trying to decode the content: " +
                             str(e) + ".")
        # Return an error message indicating that the request was malformed.
        return jsonify(error="Malformed JSON data in request",
                       original=original_text), 400

    # If message_data is None, we didn't even *try* to parse the request data
    # as JSON: this means the Content-Type wasn't set correctly.
    if message_data is None:
        return jsonify({"error": "Content-Type not set in request"}), 400

    # We can now safely add a message to the queue.
    message_queue.put(message_data)
    return jsonify({"success": "Message added successfully!"}), 200
