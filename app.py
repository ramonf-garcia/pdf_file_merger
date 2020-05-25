from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
from logging import FileHandler
import logging
from views import pdf_merger


app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_pyfile("./config/app.cfg")
app.register_blueprint(pdf_merger)
CSRFProtect(app)


@app.before_first_request
def set_logging():
    if not app.config["DEBUG"]:
        handler = FileHandler(filename=app.config["LOG_FILE"])
        handler.setFormatter = logging.Formatter(app.config["LOG_FORMAT"])
        handler.setLevel(app.config["LOG_LEVEL"])
        app.logger.addHandler(handler)


if __name__ == "__main__":
    app.secret_key = app.config["SECRET"]
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["DEBUG"])
