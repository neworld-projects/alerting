import json
from datetime import timedelta

from redis.client import Redis

from settings import redis_config


class RedisConnection(Redis):
    def get(self, name, data_type=None):
        result = super(RedisConnection, self).get(name)
        if result and data_type == 'json':
            return json.loads(result)
        return result

    def set(self, name, value, ex: None | int | timedelta = -1, px: None | int | timedelta = None, nx: bool = False,
            xx: bool = False, keepttl: bool = False, data_type=None):
        if data_type == 'json':
            value = json.dumps(value)
        return super(RedisConnection, self).set(name, value, ex, px, nx, xx, keepttl)


alert_data_cache = RedisConnection(host=redis_config.get('host'), port=redis_config.get('port'), db=0)
coins_for_call_tradingview = RedisConnection(host=redis_config.get('host'), port=redis_config.get('port'), db=1)
