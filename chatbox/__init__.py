from flask import Flask
from flask_sse import sse
app = Flask(__name__)
app.config.from_pyfile("settings.py")
app.register_blueprint(sse, url_prefix="/stream")
from . import views