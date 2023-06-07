from datetime import date
import re
import uuid
from geo.country_codes import country_codes_and_names


def member_id_clean(member_id: str) -> str:
    '''
    Helper function to trip out whitespace and ensure all caps norm.
    '''
    return member_id.strip().upper()


# Member ID Format Thoughts:
# - at first did UUID, but I want to make an easily memorizable member id pattern
# - we want to provide security/privacy, so i dont want PII in the number
# - there may be operational benefits that the ID should surround w/. ex: putting year/country/birthdate can indicate certain treatments/opportunities at a glance
# - thought about incrementing in some way from ids in the database, but we just need non-collision. order/incrementing doesnt really matter. so just ignoring current increment
# - including a dash deliminter to help people read/see in chunks and be easier to memorize
# - i don't want to reference first/last names, incase they need to change their name

def member_id_generate(year: int, country_code: str, birth_date: date) -> str:
    '''
    Input: Takes a variety of member data points
    Output: Returns a string representing the member ID for the user (non-deterministic bc of UUID selection)
    '''
    # VALIDATE
    # --- year
    if year > date.today().year:
        raise ValueError('Year cannot be in the future')
    # --- country
    if country_code not in country_codes_and_names.keys():
        raise ValueError('Not a valid country code')
    # --- birth_date
    if birth_date.year > date.today().year:
        raise ValueError('Birth year cannot be in the future')
    # GENERATE
    id_parts = [
        str(year)[-2:],
        country_code, # TODO: should we actually have country? Or is it better to hide identifying factors
        str(str(birth_date.year)[-2:]).zfill(2),
        str(birth_date.month).zfill(2), # 0 pad
        # include birth day?
        str(uuid.uuid4()).split('-')[1] # start with a random uuid, and just grab the first 4 char chunk
    ]
    # return joined parts w/ dash deliminter
    return '-'.join(id_parts).upper()


# Member ID Validation Thoughts:
# - I think the error codes only make sense internally, they'd probably confuse a user. I'd keep err responses general

def is_member_id_valid(member_id_str) -> tuple[bool, str]:
    '''
    Input: Takes a string, which should represent a Member ID.
    Output: Returns a tuple of (is_valid, error_message)
    '''
    splits = member_id_str.split('-')

    # TEST 0: Length
    if len(splits) != 5 or len(member_id_str) != 16:
        return False, 'Member ID is an incorrect length or number of segments.'
    # TEST 1: year (TODO: min/max expectation for year?)
    year_pattern = re.compile(r'^\d{2}$')
    if year_pattern.match(splits[0]) is None:
        return False, 'Incorrect year'
    # TEST 2: country code (not using pattern, just checking against our list)
    if splits[1].upper() not in country_codes_and_names.keys():
        return False, f'Incorrect country code. Got {splits[1]}'
    # --- disallow US based country codes???
    if splits[1].upper() == 'US':
        return False, f'Disallowed country code. Got {splits[1]}'
    # TEST 3: birth year (last 2 digits)
    birth_year_pattern = re.compile(r'^\d{2}$')
    if birth_year_pattern.match(splits[2]) is None:
        return False, f'Expecting 2 digit birth year. Got {splits[2]}'
    # TEST 3: birth month
    birth_year_pattern = re.compile(r'^\d{2}$')
    if birth_year_pattern.match(splits[3]) is None:
        return False, f'Expecting 2 digit birth month. Got {splits[3]}'
    # --- expect between 1-12
    if int(splits[3]) < 1 or int(splits[3]) > 12:
        return False, f'Expecting birth month between 1-12. Got {splits[3]}'
    # TEST 4: 4 alphanumeric characters
    rand_pattern = re.compile(r'^[a-zA-Z0-9]{4}$')
    if rand_pattern.match(splits[4]) is None:
        return False, f'Expected 4 alphanumeric characters. Got {splits[4]}'

    # Valid!
    return True, None

