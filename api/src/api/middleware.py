from functools import wraps
import json as json_lib
from sanic.response import json

from dbs.database_redis import Cacher

def endpoint_cache(expire: int, key_on: str = None):
    '''
    Sanic endpoint decorator request/response auto-caching.
    expire: seconds held in cache
    key_on: 'json' or 'args' or None. That can be pulled off the request obj and serialized for key
    '''
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # PARAMS/KEY
            cache_keys = ['endpoint_cache', f.__name__]
            if key_on != None:
                key_request_params = json_lib.dumps(request.args if key_on == 'args' else request.json)
                cache_keys.append(key_request_params)

            # CHECK CACHE
            cached_response = Cacher().get(cache_keys)
            # --- if cache hit, interrupt and respond with value (prior payload)
            if cached_response != None:
                print('endpoint cache hit!')
                return json(json_lib.loads(cached_response))
            
            # MISS? RESPOND
            response = await f(request, *args, **kwargs)
            # --- cache the outgoing json payload
            Cacher().set(cache_keys, json_lib.dumps(response.raw_body), ex=expire)
            # --- respond
            return response

        return decorated_function
    return decorator