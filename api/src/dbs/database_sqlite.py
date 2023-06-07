# HACK: this should be done w/ alembic outside this service, but for simplicity doing it here

async def setup_in_memory_sqlite_db(session):
    '''
    Sets up the SQLite in memory db. Doing this as a function instead of using alembic for simplicity.
    '''
    # --- drop existing table to clear data/schema
    await session.execute('''
        DROP TABLE IF EXISTS member_id;
    ''')
    # --- create/re-create table
    await session.execute('''
        CREATE TABLE IF NOT EXISTS member_id (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')
