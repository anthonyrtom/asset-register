import re

def return_csv_headers():
    data = ["Depreciation Start Date","Asset Name", "Purchase Price","Salvage Value","Useful Life","Depreciation Method","Date Format","Date Separator", "Year End"]
    return data

def return_csv_data():
    data = [["01/03/2024", "28/02/2028", "Fridge", 10000,2000, 4, "straight", 2, 28, "dmy"," ", 0], ["17/06/2024", "17/06/2024", "Motor Car", 200000,0, 5, "reducing", 2, 28, "dmy","/", 15000]]
    return data


def is_row_correctly_formatted(row):
    row_data_dict = {} 
    row_data_dict["correctly_formatted"] = True
    row_data_dict["errors"] = []
    numeric_dict = check_numeric_values(row)
    if numeric_dict["errors"]:
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].extend(row_data_dict["errors"])
    if row.get("Asset Name","") == "":
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Empty asset name")
    temp_val = row.get("Depreciation Method",None)
    if  (not temp_val) or not(temp_val.lower() in ["straight line", "reducing balance"]):
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Depreciation method not supported")
    temp_val = row.get("Date Format",None)
    if not temp_val or not(temp_val in ["dmy", "dym", "mdy", "myd", "ymd", "ydm"]):
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Date not in format supported")
    temp_val = row.get("Date Separator",None)
    if not temp_val or not(temp_val in ["/", "-", ".", " "]):
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Date separator not supported")
    temp_val = row.get("Year End",None)
    if not temp_val:
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Year End blank")
    else:
        if not year_end_correctly_formatted(temp_val):
            row_data_dict["correctly_formatted"] = False
            row_data_dict["errors"].append("Year End not in the correct format")
    return row_data_dict

def year_end_correctly_formatted(year_end):
    year_end_split = year_end.split()
    if len(year_end_split) != 2:
        return False
    try:
        day = int(year_end_split[0])
        if not isinstance(day, int):
            return False
    except ValueError:
        return False
    month = year_end_split[1].lower()
    if not (month in ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]):
        return False
    return True


def check_numeric_values(row_dict):
    errors_dict = {}
    errors_dict["errors"] = []
    for key, val in row_dict.items():
        if key in ["Useful Life", "Purchase Price", "Salvage Value"]:
            if not isinstance(val,(int, float)):
                errors_dict["errors"].append(f"{key} not a number")
    return errors_dict

def get_allowed_file_extensions():
    return ["csv", "txt"]

def allowed_file(filename):
    ALLOWED_EXTENSIONS = get_allowed_file_extensions()
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_to_file(the_message, file_name=None):

    if not file_name:
        file_name = "Logfile.txt"
    with open(file_name, "a") as logfile:
        logfile.write(f"\n {the_message} \n=========== logged\n")