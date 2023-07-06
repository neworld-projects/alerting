from bson import ObjectId

from DTOs import Alert
from mongo.select import get_alert_mongo
from settings import db


def not_exist_insert_alert_mongo(alert_data: Alert):
    result_data = db.alerts.find_one(alert_data.__dict__)
    if result_data:
        return
    result = db.alerts.insert_one(alert_data.__dict__)
    return result.inserted_id


def update_status_false(instance_id: str):
    db.alerts.update_one({'_id': ObjectId(instance_id)}, {'$set': {'status': False}})


def update_alert_mongo_with_data(alert_data: Alert):
    result = get_alert_mongo(alert_data)
    if not result:
        return
    result = db.alerts.update_one(alert_data.__dict__, {'$set': {'status': False}})
    return result
