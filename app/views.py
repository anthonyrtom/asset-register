from . import db
from flask import Blueprint, render_template, Response, request, redirect, flash, current_app
import csv, io, os
from .helpers import return_csv_headers, return_csv_data
from werkzeug.utils import secure_filename
from .models import FileUploadHistory
from .helpers import allowed_file

main = Blueprint("main",__name__)

@main.route("/", methods=["GET", "POST"])
def appload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("There seem to be no file uploaded")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        if allowed_file(filename):
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"],filename))
            extension = filename.rsplit('.', 1)[1].lower()
            try:
                saved_file = FileUploadHistory(file_name = filename, file_extension=extension)
                db.session.add(saved_file)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash("File not saved")
            return render_template("download.html")
        else:
            flash(f"File not saved, files like {filename} are not allowed")
    return render_template("index.html")

@main.route("/download_csv_sample", methods=["GET", "POST"])
def download_sample_file():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    headers = return_csv_headers()
    writer.writerow(headers)
    data = return_csv_data()
    writer.writerows(data)
    buffer.seek(0)
    return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sample_file.csv"})