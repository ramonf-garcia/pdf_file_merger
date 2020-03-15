from flask import (
    Flask,
    render_template,
    request,
    abort,
    redirect,
    flash,
    url_for,
    send_from_directory,
)
from flask_wtf.csrf import CsrfProtect
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
import logging
from logging.handlers import RotatingFileHandler
import datetime
import os
import sys

app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_pyfile("./config/app.cfg")
CsrfProtect(app)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def merge_pdfs(input_files, output_filename=None):
    input_streams = []
    if not output_filename:
        output_filename = datetime.datetime.now().strftime("%y-%m-%d_%H%M%S")
    if ".pdf" in output_filename.lower():
        output_filename = ".".join(output_filename.split(".")[:-1])
    output_filename = ".".join((output_filename, "pdf"))
    full_filename = os.path.join(app.config["DOWNLOAD_FOLDER"], output_filename)
    try:
        for input_file in input_files:
            input_streams.append(open(input_file, "rb"))
        writer = PdfFileWriter()
        with open(full_filename, "wb") as pdf_output:
            for reader in map(PdfFileReader, input_streams):
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(n))
            writer.write(pdf_output)
    except IOError as error:
        app.logger.error(f"Failed to generate file {output_filename}: {error}")
        return None
    finally:
        for f in input_streams:
            f.close()
    app.logger.info(f"{output_filename} created")
    return output_filename


def clean_uploads(filename_list):
    for filename in filename_list:
        try:
            os.remove(filename)
        except IOError as error:
            app.logger.error(f"Failed to clean file {filename}: {error}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file_list = request.files.getlist("file[]")
        output_filename = request.form.get("filename", None)
        merge_list = []

        for uploaded_file in file_list:
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                try:
                    uploaded_filename = os.path.join(
                        app.config["UPLOAD_FOLDER"], filename
                    )
                    uploaded_file.save(uploaded_filename)
                    merge_list.append(uploaded_filename)
                except IOError as error:
                    app.logger.error(f"Failed to open/save file: {error}")
                    flash(f"ERROR - Failed to save file: {filename} locally")
                    return redirect(url_for("index"))
            else:
                flash(f"ERROR - Failed to upload file: {filename}")
                return redirect(url_for("index"))
        download_filename = merge_pdfs(merge_list, output_filename)
        clean_uploads(merge_list)
        if download_filename:
            if app.config["ALLOW_DOWNLOADS"]:
                return redirect(url_for("download_file", filename=download_filename))
            else:
                flash(f"SUCCESS - File: {download_filename} generated!")
                return redirect(url_for("index"))
        else:
            app.logger.error("No download filename")
            flash("ERROR - Failed to generate file for download")
            return redirect(url_for("index"))
    else:
        return render_template("upload.html")


@app.route("/download_file/<filename>")
def download_file(filename):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename)

@app.errorhandler(404)
def page_not_found(e):
    flash("Uh oh! that page was not found")
    return render_template('index.html')

@app.errorhandler(500)
def page_not_found(e):
    flash("ERROR - It is not you, I'm a bad program")
    return render_template('index.html')

@app.before_first_request
def set_logging():
    if not app.config["DEBUG"]:
        handler = RotatingFileHandler(
            app.config["LOG_FILE"],
            maxBytes=app.config["LOG_SIZE"],
            backupCount=app.config["LOG_COUNT"]
        )
        handler.setFormatter = logging.Formatter(app.config["LOG_FORMAT"])
        handler.setLevel(app.config["LOG_LEVEL"])
        app.logger.addHandler(handler)

if __name__ == "__main__":
    app.secret_key = app.config["SECRET"]
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["DEBUG"])