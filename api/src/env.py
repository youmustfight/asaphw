import boto3
import json
import os

# ====================
# INIT
# ====================

# --- setter (aka fetch & set secrets from AWS Secrets Manager, enabling multiple target env deployments)
def _set_secrets_on_env():
    session = boto3.session.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    client = session.client(service_name='secretsmanager', region_name=os.environ.get('AWS_REGION'))
    try:
        get_secret_value_response = client.get_secret_value(SecretId=os.environ.get('TARGET_ENV'))
        # Decrypts secret using the associated KMS key.
        secret = json.loads(get_secret_value_response['SecretString'])
        for key in dict(secret).keys():
            os.environ[key] = secret[key]
    except Exception as err:
        # For a list of exceptions thrown, see https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise err

# --- getter
def _env_getter(secret_key):
    # If no secrets seen, fetch and set (will just run on first get)
    if (os.environ.get(secret_key) == None):
        _set_secrets_on_env()
    return os.environ.get(secret_key)


# ====================
# SECRETS
# ====================

# DATABASE
def env_get_database_app_user_name():
    return _env_getter('DATABASE_APP_USER_NAME')
def env_get_database_app_user_password():
    return _env_getter('DATABASE_APP_USER_PASSWORD')
def env_get_database_app_name():
    return _env_getter('DATABASE_APP_NAME')
def env_get_database_app_host():
    return _env_getter('DATABASE_APP_HOST')
def env_get_database_app_port():
    return _env_getter('DATABASE_APP_PORT')
def env_get_database_app_url(driver="asyncpg"):
    # # V1 - In-Memory SQLite
    # # In-memory sql database for SQLAlchemy. Can replace this with external databases + create other env getters.
    # # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlite
    # return 'sqlite+aiosqlite://'
    # V2 - Postgres
    return f"postgresql+{driver}://{env_get_database_app_user_name()}:{env_get_database_app_user_password()}@{env_get_database_app_host()}:{env_get_database_app_port()}/{env_get_database_app_name()}"

# ENV
def env_is_local() -> bool:
    return _env_getter('TARGET_ENV') == 'asap/local'
def env_is_production() -> bool:
    return _env_getter('TARGET_ENV') == 'asap/production'

# SERVICE - API
def env_get_service_api_host() -> str:
    return _env_getter('SERVICE_API_HOST')
def env_get_service_api_port() -> int:
    return int(_env_getter('SERVICE_API_PORT'))
def env_get_service_api_url():
    return _env_getter('SERVICE_API_URL')

# SERVICE - API CACHE (REDIS)
def env_get_service_cache_host():
    return _env_getter('SERVICE_CACHE_HOST')
def env_get_service_cache_port():
    return _env_getter('SERVICE_CACHE_PORT')


# SERVICE -- WWW
def env_get_service_www_host() -> str:
    return _env_getter('SERVICE_WWW_HOST')
def env_get_service_www_port() -> int:
    return int(_env_getter('SERVICE_WWW_PORT'))
def env_get_service_www_url():
    return _env_getter('SERVICE_WWW_URL')
