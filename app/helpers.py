def return_csv_headers():
    data = ["AcquisitionDate", "DepnStartDate","AssetName", "AssetPrice","AccumulatedDepreciation","DepreciationYears","DepreciationMethod", "YearendMonthAsNumber","YearendDay", "DateFormat","DateSeparator", "ResidualValue"]
    return data

def return_csv_data():
    data = [["01/03/2024", "01/03/2024", "Fridge", 10000,2000, 5, "straight", 2, 28, "dmy"," ", 0], ["17/06/2024", "17/06/2024", "Motor Car", 200000,0, 5, "reducing", 2, 28, "dmy","/", 15000]]
    return data

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