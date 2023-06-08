from contextvars import ContextVar
from sanic import Sanic
from sanic_cors import CORS

from api.error_handler import APIErrorHandler
import env
from dbs.routes import blueprint_database
from dbs.sa_sessions import create_sqlalchemy_session
from member_id.routes import blueprint_member_id


# INIT
app_api = Sanic('api')
# --- cors (TODO: make it restrictive to domains of frontend services)
CORS(app_api)


# MIDDLEWARE
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
_base_model_session_ctx = ContextVar('session')
@app_api.middleware('request')
async def inject_session(request):
    request.ctx.session = create_sqlalchemy_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@app_api.middleware('response')
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


# ROUTES (felt like set/list/dict was too easy, so decided to do w/ ORM example)
# --- databases
app_api.blueprint(blueprint_database)
# --- members
app_api.blueprint(blueprint_member_id)


# ERROR HANDLER
app_api.error_handler = APIErrorHandler()


# SERVER RUN
def start_api():
    host = env.env_get_service_api_host()
    port = env.env_get_service_api_port()
    app_api.run(
        host=host,
        port=port,
        auto_reload=env.env_is_local(),
        workers=2)
 