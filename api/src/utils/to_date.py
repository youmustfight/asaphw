from dateutil import parser

def to_date(date_string):
    date_string_as_datetime = parser.parse(str(date_string))
    date_string_as_date = date_string_as_datetime.date()
    return date_string_as_date
    