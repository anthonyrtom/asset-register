from datetime import datetime
import csv
import dateutil.parser
import math

def return_csv_headers():
    data = ["Depreciation Start Date","Asset Name", "Purchase Price","Accumulated Depreciation","Salvage Value","Useful Life","Depreciation Method","Year End"]
    return data

def return_csv_data():
    data = [["01/03/2024","Fridge", 10000,0,2000, 4, "straight line", "28 February"], ["17-06-2024","Motor Car", 200000,1200,0, 5, "reducing balance", "30 June",], ["17-06-2024","Lenovo Laptop", 18000,0,0, 3, "straight line", "31 December"], ["2024 1 1","Furniture", 100000,0,5000, 6.5, "straight line", "30 September"]]
    return data


def error_dict(row):
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
    temp_val = row.get("Year End",None)
    if not temp_val:
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Year End blank")
    else:
        if not year_end_correctly_formatted(temp_val):
            row_data_dict["correctly_formatted"] = False
            row_data_dict["errors"].append("Year End not in the correct format")
    strdate = row.get("Depreciation Start Date",None)
    if not strdate or (extract_date(strdate) is None):
        row_data_dict["correctly_formatted"] = False
        row_data_dict["errors"].append("Date could not be parsed correctly")
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
    months = months_list()
    if not (month in months):
        return False
    if day < 0 or day > 31:
        return False
    if month == "february" and day > 29:
        return False
    if month in ["april", "june", "september", "november"] and day > 30:
        return False
    return True


def check_numeric_values(row_dict):
    errors_dict = {}
    errors_dict["errors"] = []
    for key, val in row_dict.items():
        if key in ["Useful Life", "Purchase Price", "Salvage Value", "Accumulated Depreciation"]:
            try:
                numb_val = float(val)
            except:
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
        logfile.write(f"\n {the_message} \n=========== logged=========== \n")



def extract_date(text):
    """
    Attempts to extract a date from the given text string using various date formats.

    Args:
        text (str): The text string to search for a date.

    Returns:
        datetime.date or None: The extracted date object, or None if no date could be found.
    """

    try:
        # Try parsing the text using the dateutil.parser module, which is capable of handling many different date formats.
        date = dateutil.parser.parse(text, fuzzy=True)
        return date
    except ValueError:
        # If the dateutil parser fails, try using the datetime.strptime function with some common date formats.
        date_formats = [
            "%Y-%m-%d",  # YYYY-MM-DD
            "%d-%m-%Y",
            "%d/%m/%Y",  # DD/MM/YYYY
            "%m/%d/%Y",  # MM/DD/YYYY
            "%m-%d-%Y",
            "%B %d, %Y",  # Month Day, Year
            "%d %B %Y",  # Day Month Year
            "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
        ]

        for format in date_formats:
            try:
                date = datetime.strptime(text, format)
                return date
            except ValueError:
                pass

    return None  # If no date could be extracted, return None

def read_csv_dict_reader(filename):
    error_list = []
    depn_schelue_list = []
    try:
        openfile = open(filename)
        dict_reader = csv.DictReader(openfile)
        for row in dict_reader:
            result_dict = error_dict(row)
            if result_dict["correctly_formatted"]:
                name = row["Asset Name"]
                depn_method = row["Depreciation Method"]
                year_end = row["Year End"]
                depn_start_date = row["Depreciation Start Date"]
                depn_start_date = extract_date(depn_start_date)
                useful_life = row["Useful Life"]
                purchase_price = row["Purchase Price"]
                salvage_value = row["Salvage Value"]
                accum_depn = row["Accumulated Depreciation"]
                asset = DepreciableAsset(name=name, depn_method=depn_method, year_end=year_end,depn_start_date=depn_start_date, useful_life=useful_life, purchase_price=purchase_price, salvage_value=salvage_value, accum_depn=accum_depn)
                asset.calculate_depn_schedule()
                log_to_file(asset,"asset.txt")
                depn_schelue_list.append(asset)
            else:
                error_list.append(result_dict)
        openfile.close()
        return {"asset":depn_schelue_list, "errors":error_list}
    except Exception as e:
        log_to_file("Error", e)

def months_list():
    data = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    return data

def month_number_from_string(str_month):
    if not isinstance(str_month, str):
        return -1

    months = months_list()
    str_month = str_month.lower()

    if str_month in months:
        return months.index(str_month) + 1
    else:
        return -1

def is_leap_year(year):
    try:
        datetime(year, 2, 29)
        return True
    except ValueError:
        return False

def calculate_next_year(date_obj):
    if not isinstance(date_obj, datetime):
        raise TypeError("Not a valid date given")

    next_year = date_obj.year + 1
    curr_obj_year = date_obj.year

    # Handle leap year case for February 29
    if is_leap_year(next_year) and date_obj.month == 2 and date_obj.day == 29:
        date_obj = date_obj.replace(year=next_year, day=29)
    elif is_leap_year(curr_obj_year) and date_obj.month == 2 and date_obj.day == 29:
        date_obj = date_obj.replace(year=next_year, day=28)
    else:
        date_obj = date_obj.replace(year=next_year)
    
    return date_obj

def calculate_first_year_end(depn_start_date, year_end):
    try:
        year_end_day = int(year_end.split()[0])
        monthend = year_end.split()[1]
        int_month = month_number_from_string(monthend)
        extracted_year = depn_start_date.year
        this_year_end = datetime(extracted_year, int_month, year_end_day)
        curr_year = this_year_end.year
        if is_leap_year(this_year_end.year) and int_month == 2:
            this_year_end = datetime(depn_start_date.year, int_month, 29)
        if curr_year == depn_start_date.year and (this_year_end >= depn_start_date):
            return this_year_end
        elif curr_year > depn_start_date.year:
            next_year = curr_year + 1
            if is_leap_year(next_year) and int_month == 2:
                this_year_end = datetime(next_year, int_month, 29)
                return this_year_end
            else:
                this_year_end = datetime(next_year, int_month, year_end_day)
                return this_year_end
    except Exception as e:
        print(e)
    return None

def calculate_days_between_two_dates(first_date, second_date):
    if not isinstance(first_date,datetime) and not isinstance(second_date,datetime):
        raise TypeError("You must provide valid dates")
    date_diff = second_date - first_date
    days = date_diff.days
    return days

def calculate_depn_charge(cost, salvage, useful_life, prior_year,year_end, accum_depn, method="straight"):
    curr_year = calculate_first_year_end(prior_year, year_end)
    depn_schedule = []
    charge = 0
    book_value = cost - accum_depn
    if book_value <= salvage:
        year_data = {"year": datetime.strftime(curr_year, "%d-%m-%Y"), "depn_charge":0, "book_value":book_value}
        depn_schedule.append(year_data)
        return depn_schedule
    if isinstance(useful_life, float):
        useful_life = math.ceil(useful_life)
    for i in range(useful_life+1):
        if i == 0:
            curr_year = prior_year
            next_year = calculate_first_year_end(curr_year, year_end)
        else:
            next_year = calculate_next_year(curr_year)
        days = calculate_days_between_two_dates(curr_year,next_year)
        divisor = 365
        if is_leap_year(next_year.year):
            divisor = 366
        if method == "straight":
            charge = (cost - salvage)/useful_life * days/divisor
        else:
            nbv = cost - accum_depn
            charge = nbv/useful_life * days/divisor
        book_value = cost - accum_depn - charge
        if book_value < salvage and (cost - accum_depn)> salvage:
            charge = cost - accum_depn - salvage
            book_value = cost - accum_depn - charge
            year_data = {"year": datetime.strftime(next_year, "%d-%m-%Y"), "depn_charge":charge, "book_value":book_value}
            depn_schedule.append(year_data)
            break
        else:
            book_value = cost - accum_depn - charge
            year_data = {"year": datetime.strftime(next_year, "%d-%m-%Y"), "depn_charge":charge, "book_value":book_value}
            accum_depn += charge
            depn_schedule.append(year_data)
        curr_year = next_year
    return depn_schedule


class DepreciableAsset:
    def __init__(self,name, depn_method, year_end, depn_start_date
                 ,useful_life, purchase_price, salvage_value, accum_depn):
        self.name = name
        self.depn_method = depn_method
        self.year_end = year_end
        self.depn_start_date = depn_start_date
        self.useful_life = abs(float(useful_life))
        self.purchase_price = abs(float(purchase_price))
        self.salvage_value = abs(float(salvage_value))
        self.accum_depn = abs(float(accum_depn))
        self.depn_schedule = []
    
    def calculate_depn_schedule(self):
        if self.depn_method == "straight line":
            self.depn_schedule = calculate_depn_charge(self.purchase_price,self.salvage_value,self.useful_life,self.depn_start_date, self.year_end,self.accum_depn,self.depn_method )
        elif self.depn_method == "reducing balance":
            self.depn_schedule = calculate_depn_charge(self.purchase_price,self.salvage_value,self.useful_life,self.depn_start_date, self.year_end,self.accum_depn,self.depn_method)
            
   
    def __repr__(self):
        return (f"DepreciableAsset(name='{self.name}', depn_method='{self.depn_method}', "
                f"year_end='{self.year_end}', depn_start_date='{self.depn_start_date}', "
                f"useful_life={self.useful_life}, purchase_price={self.purchase_price}, "
                f"salvage_value={self.salvage_value}, accum_depn={self.accum_depn}, depn_schedule={self.depn_schedule})")