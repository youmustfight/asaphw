from sanic.response import json
from sanic import Blueprint

from dbs.database_sqlite import setup_in_memory_sqlite_db


# ROUTE FORK (aka 'blueprints')
blueprint_database = Blueprint("blueprint_database")


# ROUTES
@blueprint_database.route('/database/init', methods = ['POST'])
async def app_rotute_setup(request):
    """
    Endpoint: /database/init
    Description: Sets up the SQLite in memory db
    Method: GET
    Example Response: { "status": "success" }
    """
    session = request.ctx.session
    async with session.begin():
        await setup_in_memory_sqlite_db(session)
    return json({ 'status': 'success' })
