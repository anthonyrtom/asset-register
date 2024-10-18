from . import db
from flask import Blueprint, render_template, Response, request, redirect, flash, current_app, url_for, send_from_directory
import os
from .asset import return_csv_headers, return_csv_data
from werkzeug.utils import secure_filename
from .models import FileUploadHistory
from .asset import allowed_file, read_csv_dict_reader, create_csv_buffer, return_csv_buffer, unpack_dict, write_csv_to_file

main = Blueprint("main",__name__)

@main.route("/", methods=["GET", "POST"])
@main.route("/appload", methods=["GET", "POST"])
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
                    if returned_dict["errors"]:
                        unformatted_errors = returned_dict["errors"]
                        error_list = unpack_dict(unformatted_errors)
                        flash("There were errors if you are not sure of the format please download it on the link above")
                        return render_template("error_list.html", error_list=error_list)
                    else:
                        assets_list = returned_dict["asset"]
                        data, headers = return_csv_buffer(assets_list)
                        write_csv_to_file(upload_folder,headers,data)
                    flash("Operation successful")
                    return render_template("success.html")
            except Exception as e:
                db.session.rollback()
                flash("File not saved, there was an error")
                return redirect(url_for(request.url))
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash(f"That file format is not supported")
            return redirect(request.url)
    return render_template("index.html")

@main.route("/download-csv-sample", methods=["GET", "POST"])
def download_sample_file():
    headers = return_csv_headers()
    data = return_csv_data()
    buffer = create_csv_buffer(headers,data)
    return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sample_file.csv"})

@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@main.route("/download-csv-asset")
def download_csv_asset():
    folder = current_app.config["UPLOAD_FOLDER"]
    file = os.path.join(folder,"data.csv")
    if os.path.exists(file):
        return send_from_directory(folder, "data.csv", as_attachment=True, download_name="Depreciable_asset.csv")
    return redirect(request.url)

# @main.route("/", methods=["GET", "POST"])
# def appload_file():
#     returned_dict = {}
#     if request.method == "POST":
#         if "file" not in request.files:
#             flash("There seem to be no file uploaded")
#             return redirect(request.url)
#         file = request.files["file"]
#         if file.filename == "":
#             flash("No selected file")
#             return redirect(request.url)
        
#         filename = secure_filename(file.filename)
#         if allowed_file(filename):
#             upload_folder = current_app.config["UPLOAD_FOLDER"]
#             file_path = os.path.join(upload_folder,filename)
#             file.save(file_path)
#             try:
#                 extension = filename.rsplit('.', 1)[1].lower()
#                 saved_file = FileUploadHistory(file_name = filename, file_extension=extension)
#                 db.session.add(saved_file)
#                 db.session.commit()
#                 if extension == "csv":
#                     returned_dict = read_csv_dict_reader(file_path)
#                     if returned_dict["errors"]:
#                         unformatted_errors = returned_dict["errors"]
#                         error_list = unpack_dict(unformatted_errors)
#                         flash("There were errors if you are not sure of the format please download it on the link above")
#                         return render_template("error_list.html", error_list=error_list)
#                     else:
#                         assets_list = returned_dict["asset"]
#                         data, headers = return_csv_buffer(assets_list)
#                         buffer = create_csv_buffer(headers,data)
#                     flash("Operation successful")
#                     return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=depreciable_asset.csv"})
#             except Exception as e:
#                 db.session.rollback()
#                 flash("File not saved, there was an error")
#                 return redirect(url_for(request.url))
#             finally:
#                 # file_path = os.path.abspath(file)
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#         else:
#             flash(f"That file format is not supported")
#             return redirect(request.url)
#     return render_template("index.html")


