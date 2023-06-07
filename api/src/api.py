from contextvars import ContextVar
from datetime import datetime
import json as json_lib
from sanic import Request, response, Sanic
from sanic.handlers import ErrorHandler
from sanic.response import json
from sanic_cors import CORS
import sqlalchemy as sa

from dbs.sa_sessions import create_sqlalchemy_session
from dbs.redis_manager import rc
from dbs.sqlite_manager import setup_in_memory_sqlite_db
import env
from member_id.member_id_model import MemberID
from member_id.member_id_utils import is_member_id_valid, member_id_clean, member_id_generate
from utils.to_date import to_date

app = Sanic('api')


# MIDDLEWARE
# --- cors (TODO: make it restrictive to domains of frontend services)
CORS(app)
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
_base_model_session_ctx = ContextVar('session')
# --- session
@app.middleware('request')
async def inject_session(request):
    request.ctx.session = create_sqlalchemy_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@app.middleware('response')
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


# ERROR HANDLER
class CustomErrorHandler(ErrorHandler):
    def default(self, request: Request, exception: Exception):
        return json({
          "status": "failure",
          "error": str(exception),
        }, status=getattr(exception, 'status_code', 500))
app.error_handler = CustomErrorHandler()    


# ROUTES
# --- SETUP (HACK: felt like set/list/dict was too easy, so decided to do w/ ORM example)
"""
Endpoint: /database/init
Description: Sets up the SQLite in memory db
Method: GET
Example Response: { "status": "success" }
"""
@app.route('/database/init', methods = ['POST'])
async def app_rotute_setup(request):
    session = request.ctx.session
    async with session.begin():
        await setup_in_memory_sqlite_db(session)
    return json({ 'status': 'success' })


# --- MEMBER IDS
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
@app.route('/v1/member_ids', methods = ['GET'])
async def app_route_member_id_get(request):
    session = request.ctx.session
    async with session.begin():
        query_builder = sa.select(MemberID).order_by(sa.desc(MemberID.id))
        query_member_ids = await session.execute(query_builder)
        member_ids = query_member_ids.scalars().all()
    return json({
        'status': 'success',
        'data': { 'member_ids': [mid.serialize() for mid in member_ids] }
    })


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
@app.route('/v1/member_id', methods = ['POST'])
async def app_route_member_id_post(request):
    # VALIDATE
    if request.json.get('country') == None:
        raise response.HTTPResponse(status=400, body="'country' is required")
    if request.json.get('dob') == None:
        raise response.HTTPResponse(status=400, body="'dob' is required (date of birth)")
    
    # EXECUTE
    session = request.ctx.session
    async with session.begin():
        # --- form id
        new_member_id_value = member_id_generate(
            year=datetime.now().year,
            country_code=request.json.get('country'),
            birth_date=to_date(request.json.get('dob')),
        )
        # --- create new record & insert (TODO: relying on uniqueness constraint on database to throw err, could more elegantly handle)
        new_record = MemberID(value=new_member_id_value, created_at=datetime.now())
        session.add(new_record)
        return json({ 'status': 'success' })
        

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
@app.route('/v1/member_id/validate', methods = ['POST'])
async def app_route_member_id__validate_post(request):
    # VALIDATE/CLEAN
    if request.json.get('member_id') == None:
        raise ValueError("'member_id' is required")
    clean_member_id = member_id_clean(request.json.get('member_id'))

    # CACHE CHECK
    cache_data = rc.get(clean_member_id)
    if cache_data != None:
        print('cache hit!')
        return json({
            'status': 'success',
            'data': json_lib.loads(cache_data)
        })
    
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
        # --- update cache (cast to string for serialization, set 10 sec expiration)
        rc.set(clean_member_id, json_lib.dumps(response_data), ex=10)
        # --- respond
        return json({
            'status': 'success',
            'data': response_data,
        })


# SERVER
def start_api():
    host = env.env_get_service_api_host()
    port = env.env_get_service_api_port()
    app.run(
        host=host,
        port=port,
        auto_reload=env.env_is_local(),
        workers=2)
 