from sanic.response import json
from sanic import Blueprint

from dbs.database_postgres import setup_postgres_db_tables


# ROUTE FORK (aka 'blueprints')
blueprint_database = Blueprint("blueprint_database")


# ROUTES
@blueprint_database.route('/database/init', methods = ['POST'])
async def app_rotute_setup(request):
    """
    Endpoint: /database/init
    Description: Sets up tables on either Postgres/SQLite(in memory)
    Method: GET
    Example Response: { "status": "success" }
    """
    session = request.ctx.session
    async with session.begin():
        await setup_postgres_db_tables(session)
    return json({ 'status': 'success' })
