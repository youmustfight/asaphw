from contextvars import ContextVar
from sanic import Request, Sanic
from sanic.handlers import ErrorHandler
from sanic.response import json
from sanic_cors import CORS

import env
from dbs.routes import blueprint_database
from dbs.sa_sessions import create_sqlalchemy_session
from member_id.routes import blueprint_member_id


# INIT
app = Sanic('api')
# --- cors (TODO: make it restrictive to domains of frontend services)
CORS(app)


# MIDDLEWARE
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
_base_model_session_ctx = ContextVar('session')
@app.middleware('request')
async def inject_session(request):
    request.ctx.session = create_sqlalchemy_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@app.middleware('response')
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


# ROUTES (felt like set/list/dict was too easy, so decided to do w/ ORM example)
# --- databases
app.blueprint(blueprint_database)
# --- members
app.blueprint(blueprint_member_id)


# ERROR HANDLER
class CustomErrorHandler(ErrorHandler):
    def default(self, request: Request, exception: Exception):
        return json(
            { "status": "failure", "error": str(exception) },
            status=getattr(exception, 'status_code', 500))
app.error_handler = CustomErrorHandler()    


# SERVER RUN
def start_api():
    host = env.env_get_service_api_host()
    port = env.env_get_service_api_port()
    app.run(
        host=host,
        port=port,
        auto_reload=env.env_is_local(),
        workers=2)
 