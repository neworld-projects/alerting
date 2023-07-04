from decouple import config
from pymongo import MongoClient

telegram_token = config("TELEGRAM_TOKEN")

redis_config = {
    'host': config('REDIS_HOST', default='redis_db'),
    'port': config('REDIS_PORT', default='6379')
}

client = MongoClient(config('MONGODB_URL'))
db = client.alerting

TRADINGVIEW_WEBSOCKET_URL = config('TRADINGVIEW_WEBSOCKET_URL')
AUTH_TOKEN = config('AUTH_TOKEN')
TRADINGVIEW_USERNAME = config('TRADINGVIEW_USERNAME')
