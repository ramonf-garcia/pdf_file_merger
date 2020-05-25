from flask import (
    render_template,
    request,
    abort,
    redirect,
    flash,
    url_for,
    send_from_directory,
    Blueprint
)
import os
import logging
from control import (
    merge_pdfs,
    clean_uploads,
    allowed_file,
    save_files
)

UPLOADS = "uploads"
DOWNLOADS = "downloads"
EXTENSION = "pdf"

pdf_merger = Blueprint("pdf_merger", __name__)

@pdf_merger.route("/")
def index():
    return render_template("index.html")


@pdf_merger.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file_list = request.files.getlist("file[]")
        output_filename = request.form.get("filename", None)
        merge_list = []
        if len(file_list) < 2:
            logging.error("Only one file was provided, nothing to merge")
            flash("ERROR - You need to send more than one file for merge to make sense")
            return redirect(url_for("index"))
        merge_list, error = save_files(file_list, EXTENSION, UPLOADS)
        if error:
            flash(error)
            return redirect(url_for("index"))
        download_filename, error = merge_pdfs(merge_list, EXTENSION, DOWNLOADS, output_filename)
        clean_uploads(merge_list)
        if not error:
            flash(f"SUCCESS - File: {download_filename} generated!")
            return redirect(url_for("pdf_merger.download_file", filename=download_filename))
        else:
            logging.error("Merge did not return a filename, something went wrong")
            if not error:
               flash(f"ERROR - {error}")
            return redirect(url_for("index"))
    else:
        return render_template("upload.html")


@pdf_merger.route("/download_file/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOADS, filename)


@pdf_merger.errorhandler(400)
def page_not_found(e):
    flash("Uh oh! that was a bad request, try starting from scratch!")
    return render_template("index.html")


@pdf_merger.errorhandler(404)
def page_not_found(e):
    flash("Uh oh! that page was not found, check your addressbar!")
    return render_template("index.html")


@pdf_merger.errorhandler(500)
def page_not_found(e):
    flash("ERROR - It is not you, I'm a bad program and I failed to save your files")
    return render_template("index.html")
