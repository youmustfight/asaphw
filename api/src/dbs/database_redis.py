import redis
import env

redis_client = redis.Redis(
    host=env.env_get_service_cache_host(),
    port=env.env_get_service_cache_port(),
    db=0,
    decode_responses=True,
)

class Cacher:
    '''
    Redis client wrapper with convenience methods to namespace get/set keys
    '''
    client = redis_client

    def namespace_key(self, key_tree: list[str or int]) -> str:
        '''
        Join together a string of strings/ints so multiple publishers to redis don't collide
        '''
        if len(key_tree) < 2:
            raise ValueError('Not enough specificity for redis key. Collisions can occur')
        return ':::'.join(key_tree)

    def get(self, key_tree):
        print('get', key_tree)
        return self.client.get(self.namespace_key(key_tree))

    def set(self, key_tree: list[str or int], value: str, ex=None):
        print('set', key_tree)
        return self.client.set(self.namespace_key(key_tree), value, ex=ex)



