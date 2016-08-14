from flask import request, Response, jsonify

from . import app
from .messages import RedisMessageServer


@app.route("/messages", methods=["POST"])
def add_message():
    """
    Adds a message to the list of messages, as well as notifying our
    subscribers.
    """
    messages = RedisMessageServer()
    messages.add_message(request.get_json())  # Todo: JSON error-checking.
    return jsonify(success=True)


@app.route("/messages/subscribe")
def stream_messages():
    """Return an event-stream for the latest messages."""
    message_stream = RedisMessageServer().event_stream
    return Response(message_stream, mimetype="text/event-stream")


@app.route("/messages")
def get_messages():
    """Return the `max` latest messages by querying the Redis message list."""
    max_messages = request.args.get("max", app.config["MAX_MESSAGES"])
    messages = RedisMessageServer().get_messages(int(max_messages))
    return jsonify(list(messages))


@app.route("/")
def index():
    """Return the homepage; a static HTML file with some JavaScript."""
    return app.send_static_file("index.html")
