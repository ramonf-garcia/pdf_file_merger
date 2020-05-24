from flask import (
    render_template,
    request,
    abort,
    redirect,
    flash,
    url_for,
    send_from_directory,
)
from werkzeug.utils import secure_filename
import os
from control import merge_pdfs, clean_uploads, allowed_file
from app import app


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file_list = request.files.getlist("file[]")
        output_filename = request.form.get("filename", None)
        merge_list = []
        if len(file_list) < 2:
            app.logger.error("Only one file was provided, nothing to merge")
            flash("ERROR - You need to send more than one file for merge to make sense")
            return redirect(url_for("index"))
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

        download_filename, error = merge_pdfs(merge_list, output_filename)
        clean_uploads(merge_list)
        if download_filename and not error:
            if app.config["ALLOW_DOWNLOADS"]:
                return redirect(url_for("download_file", filename=download_filename))
            else:
                flash(f"SUCCESS - File: {download_filename} generated!")
                return redirect(url_for("index"))
        else:
            app.logger.error("Merge did not return a filename, something went wrong")
            if not error:
                error = "Failed to generate file for download"
            flash(f"ERROR - {error}")
            return redirect(url_for("index"))
    else:
        return render_template("upload.html")


@app.route("/download_file/<filename>")
def download_file(filename):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename)


@app.errorhandler(400)
def page_not_found(e):
    flash("Uh oh! that was a bad request, try starting from scratch!")
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    flash("Uh oh! that page was not found, check your addressbar!")
    return render_template("index.html")


@app.errorhandler(500)
def page_not_found(e):
    flash("ERROR - It is not you, I'm a bad program and I failed to save your files")
    return render_template("index.html")
