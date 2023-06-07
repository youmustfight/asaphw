import redis
import env

# TODO: check if connection open/close is problematic
redis_client = redis.Redis(
    host=env.env_get_service_cache_host(),
    port=env.env_get_service_cache_port(),
    db=0,
    decode_responses=True,
)
