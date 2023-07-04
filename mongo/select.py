from DTOs import Alert
from settings import db


def get_alert_mongo(alert_data: Alert):
    result = db.alerts.find_one(alert_data.__dict__)
    return result


def get_alerts_mongo():
    result = db.alerts.find({'status': True})
    return result


def get_symbols_mongo():
    result = db.alerts.find({'status': True}).distinct('coin_id')
    return result
