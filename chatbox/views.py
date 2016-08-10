from . import app


@app.route("/")
def index():
    """The main page of the application."""
    return app.send_static_file("index.html")
