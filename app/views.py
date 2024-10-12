from . import db
from flask import Blueprint, render_template, Response, request, redirect, flash, current_app, url_for
import csv,os
from .asset import return_csv_headers, return_csv_data
from werkzeug.utils import secure_filename
from .models import FileUploadHistory
from .asset import allowed_file, read_csv_dict_reader, DepreciableAsset, create_csv_buffer, log_to_file

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
            op_success = True
            try:
                extension = filename.rsplit('.', 1)[1].lower()
                saved_file = FileUploadHistory(file_name = filename, file_extension=extension)
                db.session.add(saved_file)
                db.session.commit()
                if extension == "csv":
                    returned_dict = read_csv_dict_reader(file_path)
                    if returned_dict["errors"]:
                        op_success = False
                        error_list = returned_dict["errors"]
                        flash("There were errors check the download")
                        return render_template("download.html", op_success = op_success, error_list=error_list)
                    else:
                        assets_list = returned_dict["asset"]
                        # log_to_file(assets_list, "asset.txt")
                        data = []
                        csv_headers = DepreciableAsset.get_sorted_years(assets_list)
                        headers = ["Name", "Depn Method", "Year End", "Depn Start Date", "Useful Life", "Purchase Price", "Salvage Value"]
                        str_headers = [dt.strftime("%d-%m-%Y") for dt in csv_headers]
                        for header in str_headers:
                            headers.append(f"Depn_Charge {header}")
                            headers.append(f"Book_Value {header}")
                        for asset in assets_list:
                            asset_dep_schedule = asset.depn_schedule
                            asset_list = [asset.name, asset.depn_method, asset.year_end, asset.depn_start_date.strftime("%d-%m-%Y"), str(asset.useful_life), str(asset.purchase_price), str(asset.salvage_value)]
                            asset_data = []
                            asset_data.extend(asset_list)
                            years_items = [item["year"] for item in asset_dep_schedule]
                            charge_list = [item["depn_charge"] for item in asset_dep_schedule]
                            book_value_list = [item["book_value"] for item in asset_dep_schedule]
                            i = 0
                            while i < len(str_headers):
                                single_date = csv_headers[i]
                                single_date = single_date.strftime("%d-%m-%Y")
                                if single_date in years_items:
                                    index = years_items.index(single_date)
                                    charge = charge_list[index]
                                    book_value = book_value_list[index]
                                    asset_data.append(charge)
                                    asset_data.append(book_value)
                                else:
                                    asset_data.append(0)
                                    asset_data.append(0)
                                i += 1
                            data.append(asset_data)

                        # log_to_file(data, "data.txt")
                        buffer = create_csv_buffer(headers,data)
                    flash("Operation successful")
                    # return render_template("download.html", op_success = op_success)
                    return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=depreciable_asset.csv"})
            except Exception as e:
                db.session.rollback()
                flash("File not saved, there was an error")
                print(e)
                return redirect(url_for(request.url))
        else:
            flash(f"File not saved, files of type like {filename} are not allowed, please change")
            return redirect(request.url)
    return render_template("index.html")

# @main.route("/download-csv-sample", methods=["GET", "POST"])
# def download_sample_file():
#     buffer = io.StringIO()
#     writer = csv.writer(buffer)
#     headers = return_csv_headers()
#     writer.writerow(headers)
#     data = return_csv_data()
#     writer.writerows(data)
#     buffer.seek(0)
#     return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sample_file.csv"})

@main.route("/download-csv-sample", methods=["GET", "POST"])
def download_sample_file():
    headers = return_csv_headers()
    data = return_csv_data()
    buffer = create_csv_buffer(headers,data)
    return Response(buffer, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sample_file.csv"})

@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")