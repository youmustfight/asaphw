from datetime import datetime
from sanic.response import json
from sanic import Blueprint
import sqlalchemy as sa

from api.middleware import endpoint_cache
from member_id.member_id_models import MemberID
from member_id.member_id_utils import is_member_id_valid, member_id_clean, member_id_generate
from user.user_models import User
from utils.to_date import to_date
from utils.validators import is_valid_country_code, is_valid_date, is_valid_nonempty_str


# ROUTE FORK (aka 'blueprints')
blueprint_member_id = Blueprint("blueprint_member_id")


# ROUTES
@blueprint_member_id.route('/v1/member_ids', methods = ['GET'])
@endpoint_cache(expire=2)
async def app_route_member_id_get(request):
    """
    Endpoint: /v1/member_ids
    Description: Gets all member ids models
    Method: GET
    Example Response: {
        "status": "success"
        "data": {
            "member_ids": [...]
        }
    }
    """
    session = request.ctx.session
    async with session.begin():
        query_builder = sa.select(MemberID).order_by(sa.desc(MemberID.id))
        query_member_ids = await session.execute(query_builder)
        member_ids = query_member_ids.scalars().all()
    # --- respond
    return json({
        'status': 'success',
        'data': { 'member_ids': [mid.serialize() for mid in member_ids] }
    })


@blueprint_member_id.route('/v1/member_id', methods = ['POST'])
async def app_route_member_id_post(request):
    """
    Endpoint: /v1/member_id
    Description: Creates a new member id model
    Method: POST
    Example Request Body: {
        "first_name": "Jose",
        "last_name": "Vasconcelos",
        "dob": "01/01/1961",
        "country": "MX"
    }
    Example Response: {
        "status": "success"
    }
    """
    # VALIDATE
    if is_valid_nonempty_str(request.json.get('first_name'), raise_if_fail=False) == False:
        raise ValueError("'first_name' is required")
    if is_valid_nonempty_str(request.json.get('last_name'), raise_if_fail=False) == False:
        raise ValueError("'last_name' is required")
    if is_valid_country_code(request.json.get('country'), raise_if_fail=False) == False:
        raise ValueError("'country' is required")
    if is_valid_date(request.json.get('dob'), raise_if_fail=False) == False:
        raise ValueError("'dob' is required (date of birth)")

    # EXECUTE
    session = request.ctx.session
    async with session.begin():
        # --- form id
        new_member_id_value = member_id_generate(
            year=datetime.now().year,
            country_code=request.json.get('country'),
            birth_date=to_date(request.json.get('dob')),
        )
        # --- if we were able to form a member ID value, let's first create a new user (if any of this errs, we rollback automatically)
        new_user_and_member_id_record = User(
            first_name=request.json.get('first_name'),
            last_name=request.json.get('last_name'),
            date_of_birth=to_date(request.json.get('dob')),
            origin_country_code=request.json.get('country'),
            created_at=datetime.now(),
            # create the related record as we insert user, so the appropriate foreign keys are set
            member_id=[MemberID(
                value=new_member_id_value,
                created_at=datetime.now(),
            )]
        )
        session.add(new_user_and_member_id_record)
        # --- respond
        return json({ 'status': 'success' })
        

@blueprint_member_id.route('/v1/member_id/validate', methods = ['POST'])
@endpoint_cache(expire=30, key_on='json')
async def app_route_member_id__validate_post(request):
    """
    Endpoint: /v1/member_id/validate
    Description: Validates a member id (and also shows if it exist's been registered by someone)
    Method: POST
    Example Request Body: {
        "member_id": "XYZ123"
    }
    Example Response: {
        "status": "success"
        "data": {
            "is_registered": true,
            "is_valid": true,
            "invalid_reason": "...",
        }
    }
    """
    # VALIDATE/CLEAN
    if is_valid_nonempty_str(request.json.get('member_id'), raise_if_fail=False) == False:
        raise ValueError("'member_id' is required")
    clean_member_id = member_id_clean(request.json.get('member_id'))
    
    # EXECUTE
    session = request.ctx.session
    async with session.begin():        
        # --- check if is a valid format
        is_valid, invalid_reason = is_member_id_valid(clean_member_id)
        # --- check if exists in db already (not 'invalid' per se, but extra meta info to show on frontend)
        query_member_id = await session.execute(
            sa.select(MemberID).where(MemberID.value == clean_member_id))
        found_member_id = query_member_id.scalar_one_or_none()
        # --- setup response payload
        response_data = {
            'is_registered': found_member_id is not None,
            'is_valid': is_valid, # True/False
            'invalid_reason': invalid_reason, # None/str
        }
        # --- respond
        return json({
            'status': 'success',
            'data': response_data,
        })
