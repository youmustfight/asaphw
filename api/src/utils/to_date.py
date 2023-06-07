from datetime import datetime


 # TODO: VERY BRITLE
def to_date(date_string):
    date_string_as_datetime = datetime.strptime(str(date_string), '%d/%m/%Y')
    date_string_as_date = date_string_as_datetime.date()
    return date_string_as_date
    