from flask import Flask
from flask_wtf.csrf import CsrfProtect
import os
from logging.handlers import RotatingFileHandler
import logging


app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_pyfile("./config/app.cfg")
CsrfProtect(app)


@app.before_first_request
def set_logging():
    if not app.config["DEBUG"]:
        handler = RotatingFileHandler(
            os.path.join(app.config["LOGGING_FOLDER"], app.config["LOG_FILE"]),
            maxBytes=app.config["LOG_SIZE"],
            backupCount=app.config["LOG_COUNT"],
        )
        handler.setFormatter = logging.Formatter(app.config["LOG_FORMAT"])
        handler.setLevel(app.config["LOG_LEVEL"])
        app.logger.addHandler(handler)


from views import *

if __name__ == "__main__":
    app.secret_key = app.config["SECRET"]
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["DEBUG"])
