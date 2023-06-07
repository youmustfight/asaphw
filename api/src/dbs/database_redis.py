import redis
import env

# TODO: check if connection open/close is problematic
redis_client = redis.Redis(
    host=env.env_get_service_cache_host(),
    port=env.env_get_service_cache_port(),
    db=0,
    decode_responses=True,
)

def r_key(list_of_values: list[str or int]) -> str:
    '''
    Join together a string of strings/ints so multiple publishers to redis don't collide
    '''
    if len(list_of_values) < 2:
        raise ValueError('Not enough specificity for redis key. Collisions can occur')
    return ':::'.join(list_of_values)
