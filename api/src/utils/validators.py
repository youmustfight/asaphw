import datetime

from geo.country_codes import country_codes_and_names
from utils.to_date import to_date


def is_valid_nonempty_str(string: str, should_raise=True) -> bool:
    '''Empty string check for use in endpoints & models (a bit trivial but helpful)'''
    if string == None or len(string) == 0:
        if should_raise == True:
            raise f'Non-empty string expected'
        else:
            return False
    return True

def is_valid_date(date_or_string_or_num: datetime or str or int, should_raise=True) -> bool:
    '''Date validation check for use in endpoints & models'''
    try:
        to_date(date_or_string_or_num) # no need to use, just need to see if it throws
        return True
    except:
        if should_raise == True:
            raise f'Invalid date'
        return False

def is_valid_country_code(country_code: str, should_raise=True) -> bool:
    '''Country Code validation check for use in endpoints & models'''
    err_msg = None
    if len(country_code) != 2:
        err_msg = f'Invalid country code length: ({len(country_code)})'
    if country_code not in country_codes_and_names.keys():
        err_msg = f'Country code not found'
    # raise!
    if err_msg == None:
        return True
    elif should_raise == True:
        raise err_msg
    else:
        return False
