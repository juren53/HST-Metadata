def convert_date(date_str):
    year = date_str.split(".")[1].strip()
    return f"{year}-00-00"

date = "ca.1968"
converted_date = convert_date(date)
print(date,converted_date)

