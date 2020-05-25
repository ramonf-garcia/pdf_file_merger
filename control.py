import datetime
import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
from werkzeug.utils import secure_filename
import logging


def allowed_file(filename, extension):
    """Validate the filename is using the allowed extension"""
    return filename.split(".")[-1] == extension


def save_files(file_list, extension, uploads):
    """Save the uploaded files if they are valid"""
    merge_list = []
    for uploaded_file in file_list:
        if uploaded_file and allowed_file(uploaded_file.filename, extension):
            filename = secure_filename(uploaded_file.filename)
            try:
                uploaded_filename = os.path.join(
                    uploads,
                    filename
                )
                uploaded_file.save(uploaded_filename)
                merge_list.append(uploaded_filename)
            except IOError as error:
                logging.error(f"Failed to open/save file: {error}")
                return None, f"ERROR - Failed to save file: {filename} locally"
        else:
            return None, f"ERROR - Failed to upload file: {filename}"
    return merge_list, None

def merge_pdfs(input_files, extension, downloads, output_filename=None):
    """Join all the files in a list and save those to the filename in the output_filename"""
    input_streams = []
    if not output_filename:
        return None, "No output filename was provided"
    if extension in output_filename.lower():
        output_filename = ".".join(output_filename.split(".")[:-1])
    output_filename = ".".join((output_filename, extension))
    full_filename = os.path.join(downloads, output_filename)
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
            logging.error(f"Failed to generate file {output_filename}: {error}")
            return None, "Could not save the merged file"
    except Exception as error:
        logging.error(f"Failed to read PDF files: {error}")
        return (
            None,
            "Could not read uploaded files correctly, validate they are not corrupted",
        )
    logging.info(f"{output_filename} created")
    return output_filename, None


def clean_uploads(filename_list):
    """Clean the uploaded files to prevent misusing them on other uploads"""
    for filename in filename_list:
        try:
            os.remove(filename)
        except IOError as error:
            logging.error(f"Failed to clean file {filename}: {error}")
