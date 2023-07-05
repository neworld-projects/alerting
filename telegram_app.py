from datetime import datetime, timezone

from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes

from DTOs import Alert
from helper.redis_connection import coins_for_call_tradingview, alert_data_cache
from mongo.insert import not_exist_insert_alert_mongo, update_status_false, update_alert_mongo_with_data
from mongo.select import get_alert_mongo, get_symbols_mongo, get_alerts_mongo
from settings import telegram_token


async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_alert_data = Alert(
        coin_id=context.args[0].upper(),
        value=float(context.args[1]),
        chat_id=update.effective_chat.id
    )

    result = not_exist_insert_alert_mongo(set_alert_data)
    if not result:
        message = f"you have already set it up alert on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"
    else:
        sync_mongo_and_redis()
        message = f"Ok i'll setup an alert on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"

    await update.message.reply_text(message, parse_mode='HTML')


async def get_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_alert_data = Alert(
        coin_id=context.args[0].upper(),
        value=float(context.args[1]),
        chat_id=update.effective_chat.id
    )

    alert_data = get_alert_mongo(set_alert_data)

    if not alert_data:
        message = f"you have <b>not</b> alert on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"
    else:
        message = f"you have one alert on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"

    await update.message.reply_text(message, parse_mode='HTML')


async def delete_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_alert_data = Alert(
        coin_id=context.args[0].upper(),
        value=float(context.args[1]),
        chat_id=update.effective_chat.id
    )

    alert_data = update_alert_mongo_with_data(set_alert_data)

    if not alert_data:
        message = f"you have <b>not</b> alert on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"
    else:
        message = f"your alert deleted on <b>{set_alert_data.value}</b> for <b>{set_alert_data.coin_id}</b>"

    await update.message.reply_text(message, parse_mode='HTML')


async def get_all_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    alerts = get_alerts_mongo()
    beautify_alerts = "\n".join([f'{alert.get("coin_id")}: {alert.get("value")}' for alert in alerts])
    message = f"all alerts:\n{beautify_alerts}"

    await update.message.reply_text(message, parse_mode='HTML')


async def send_message_telegram(alert_data: Alert):
    app = ApplicationBuilder().token(telegram_token).build()
    await app.bot.send_message(
        chat_id=alert_data.chat_id,
        text=f'<b>{alert_data.coin_id}</b>\n '
             f'you have an alert at <b>{alert_data.value}</b>\n '
             f'on <b>{datetime.now(tz=timezone.utc).__str__()}</b>',
        parse_mode='HTML'
    )


def sync_mongo_and_redis():
    coins_for_call_tradingview.set('symbols', get_symbols_mongo(), data_type='json')
    alerts = []
    for alert in get_alerts_mongo():
        alerts.append({
            'mongo_id': alert.get('_id', '').__str__(),
            'coin_id': alert.get('coin_id'),
            'chat_id': alert.get('chat_id'),
            'value': alert.get('value', 0),
            'status': alert.get('status', True)
        })
    alert_data_cache.set('alerts', alerts, data_type='json')


def main():
    sync_mongo_and_redis()
    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("set_alert", set_alert))
    app.add_handler(CommandHandler("get_alert", get_alert))
    app.add_handler(CommandHandler("get_all_alerts", get_all_alerts))
    app.add_handler(CommandHandler("delete_alert", delete_alert))

    app.run_polling()


if __name__ == '__main__':
    main()
