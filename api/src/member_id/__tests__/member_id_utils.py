import pytest
from member_id.member_id_utils import member_id_clean, member_id_generate, is_member_id_valid
from utils.to_date import to_date


def test_member_id_clean():
    # --- tests
    assert member_id_clean(' 23-MX-61-01-2F0D ') == '23-MX-61-01-2F0D', 'Spaces not trimmed'
    assert member_id_clean('23-mX-61-01-2f0d') == '23-MX-61-01-2F0D', 'Incorrect capitlization'


def test_member_id_generate():
    # --- tests: pass
    test_member_id = member_id_generate(
        year=2023,
        country_code='MX',
        birth_date=to_date('01/01/1961'),
    )
    assert len(test_member_id) == 16, 'Incorrect length'
    assert len(test_member_id.split('-')) == 5, 'Incorrect segments'
    # --- tests: fails
    try:
        member_id_generate(
            year=2023,
            country_code='MX',
            birth_date=to_date('13/13/5001'), # <-- will cause err throw
        )
    except Exception as e:
        assert "time data '13/13/5001' does not match format '%d/%m/%Y'" in str(e), 'Error not thrown for bad data'


def test_is_member_id_valid():
    # --- tests: passing
    is_valid, reason = is_member_id_valid('23-MX-61-01-2F0D')
    assert is_valid == True, 'Should have been valid'

    # --- tests: fail - length
    is_valid, reason = is_member_id_valid('23-MX-61-01-2F0D-12345')
    assert is_valid == False, 'Should fail because of extra characters'

    # --- tests: fail - country code
    is_valid, reason = is_member_id_valid('23-OP-61-01-2F0D')
    assert is_valid == False and 'OP' in reason, 'Should fail because of unknown country'
    is_valid, reason = is_member_id_valid('23-US-61-01-2F0D')
    assert is_valid == False and 'US' in reason, 'Should fail because of US'

    # --- tests: fail - month/days
    is_valid, reason = is_member_id_valid('23-MX-aa-01-2F0D')
    assert is_valid == False and 'aa' in reason, 'Should fail because of year letters'
    is_valid, reason = is_member_id_valid('23-MX-61-bb-2F0D')
    assert is_valid == False and 'bb' in reason, 'Should fail because of month letters'

    # --- tests: fail - final alphanumeric
    is_valid, reason = is_member_id_valid('23-MX-61-01-!!!!')
    assert is_valid == False and '!!!!' in reason, 'Should fail because of special characters in final part'

