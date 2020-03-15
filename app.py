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
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
import datetime
import os
import sys

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def merge_pdfs(input_files):
    input_streams = []
    timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H%M%S.pdf")
    output_file = f"./downloads/{timestamp}"
    try:
        for input_file in input_files:
            input_streams.append(open(input_file, "rb"))
        writer = PdfFileWriter()
        with open(output_file, "wb") as pdf_output:
            for reader in map(PdfFileReader, input_streams):
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(n))
            writer.write(pdf_output)
    except IOError:
        return None
    finally:
        for f in input_streams:
            f.close()
    return timestamp


def clean_uploads(filename_list):
    for filename in filename_list:
        try:
            os.remove(filename)
        except IOError:
            print(f"Failed to clean file {filename}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file_list = request.files.getlist("file[]")
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
                except IOError:
                    flash(f"Failed to save file: {filename} locally")
                    return redirect(url_for("index"))
            else:
                flash(f"Failed to upload file: {filename}")
                return redirect(url_for("index"))
        download_filename = merge_pdfs(merge_list)
        clean_uploads(merge_list)
        if download_filename:
            return redirect(url_for("download_file", filename=download_filename))
        else:
            flash("Failed to generate file for download")
            return redirect(url_for("index"))
    else:
        return render_template("upload.html")


@app.route("/download_file/<filename>")
def download_file(filename):
    return send_from_directory("./downloads", filename)


if __name__ == "__main__":
    app.secret_key = b'PEPINASUPERSECR3TKEY'
    app.run(port=1234, debug=True)
