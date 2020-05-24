import datetime
import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
from app import app


def allowed_file(filename):
    """Validate the filename is using the allowed extension"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def merge_pdfs(input_files, output_filename=None):
    """Join all the files in a list and save those to the filename in the output_filename"""
    input_streams = []
    if not output_filename:
        output_filename = datetime.datetime.now().strftime("%y-%m-%d_%H%M%S")
    if ".pdf" in output_filename.lower():
        output_filename = ".".join(output_filename.split(".")[:-1])
    output_filename = ".".join((output_filename, "pdf"))
    full_filename = os.path.join(app.config["DOWNLOAD_FOLDER"], output_filename)
    try:
        output_writer = PdfFileWriter()
        for input_file in input_files:
            reader = PdfFileReader(input_file)
            for page in range(reader.getNumPages()):
                output_writer.addPage(reader.getPage(page))
        try:
            with open(full_filename, "wb") as output:
                output_writer.write(output)
        except IOError as error:
            app.logger.error(f"Failed to generate file {output_filename}: {error}")
            return None, "Could not save the merged file"
    except Exception as error:
        app.logger.error(f"Failed to read PDF files: {error}")
        return (
            None,
            "Could not read uploaded files correctly, validate they are not corrupted",
        )
    app.logger.info(f"{output_filename} created")
    return output_filename, None


def clean_uploads(filename_list):
    """Clean the uploaded files to prevent misusing them on other uploads"""
    for filename in filename_list:
        try:
            os.remove(filename)
        except IOError as error:
            app.logger.error(f"Failed to clean file {filename}: {error}")
