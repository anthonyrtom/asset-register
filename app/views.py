from . import db
from flask import Blueprint, render_template, Response, request, redirect, flash, current_app, url_for
import csv, io, os
from .asset import return_csv_headers, return_csv_data
from werkzeug.utils import secure_filename
from .models import FileUploadHistory
from .asset import allowed_file, read_csv_dict_reader

main = Blueprint("main",__name__)

@main.route("/", methods=["GET", "POST"])
def appload_file():
    returned_dict = {}
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
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            file_path = os.path.join(upload_folder,filename)
            file.save(file_path)
            
            try:
                extension = filename.rsplit('.', 1)[1].lower()
                saved_file = FileUploadHistory(file_name = filename, file_extension=extension)
                db.session.add(saved_file)
                db.session.commit()
                if extension == "csv":
                    returned_dict = read_csv_dict_reader(file_path)
                    flash("Operation successful")
                    return render_template("download.html", returned_dict=returned_dict)
            except Exception:
                db.session.rollback()
                flash("File not saved, there was an error")
                return redirect(url_for(request.url))
        else:
            flash(f"File not saved, files like {filename} are not allowed")
            return redirect(request.url)
    return render_template("index.html")

@main.route("/download-csv-sample", methods=["GET", "POST"])
def download_sample_file():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    headers = return_csv_headers()
    writer.writerow(headers)
    data = return_csv_data()
    writer.writerows(data)
    buffer.seek(0)
    return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sample_file.csv"})

@main.route("/download-file", methods=["GET"])
def download_file():
    return render_template("download.html")