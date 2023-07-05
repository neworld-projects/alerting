import asyncio
import logging
from time import sleep

from DTOs import TradingViewData, Alert
from helper.exceptions_class import ReRunSocketException
from helper.redis_connection import coins_for_call_tradingview, alert_data_cache
from mongo.insert import update_status_false
from telegram_app import send_message_telegram, sync_mongo_and_redis
from tradingview_socket.websocket import OpenWebsocketConnection

logging.basicConfig(level=logging.INFO)


class WebSocketConnectionChart(OpenWebsocketConnection):

    def __init__(self):
        symbols = coins_for_call_tradingview.get('symbols', data_type='json')
        if not symbols:
            logging.info("can not get data from redis")
            raise ReRunSocketException
        super(WebSocketConnectionChart, self).__init__(
            symbols,
            {"name": "120", "timestamp": 7200},
        )
        self.ws_app.run_forever()

    def check_symbols(self):
        new_symbols = coins_for_call_tradingview.get('symbols', data_type='json')
        if new_symbols != self.symbols:
            self.ws_app.close()
            raise ReRunSocketException

    @staticmethod
    def check_alert(data: TradingViewData, coin_name: str):
        alerts = alert_data_cache.get('alerts', data_type='json')
        for alert in alerts:
            if alert.get('coin_id') == coin_name and data.high >= alert.get('value') >= data.low:
                logging.info(f'valid alert: {alert}')
                asyncio.run(
                    send_message_telegram(Alert(alert.get('coin_id'), alert.get('value'), alert.get('chat_id')))
                )
                update_status_false(alert.get('mongo_id'))
                sync_mongo_and_redis()

    def on_message(self, ws, message):
        try:
            self.check_symbols()
            results = super(WebSocketConnectionChart, self).on_message(ws, message)
            if results is None:
                return results
            for result in results:
                if result.get('m') == 'du':
                    data = result.get('p')[1]
                    for coin_key, coin_name in self.coin_map.items():
                        if data.get(coin_key):
                            self.check_alert(
                                TradingViewData(*data[coin_key]['s'][-1]['v'][:5]),
                                coin_name
                            )

        except Exception as e:
            logging.error(e)


def main():
    while True:
        try:
            WebSocketConnectionChart()
        except ReRunSocketException:
            sleep(30)
            logging.info("rerun")


if __name__ == '__main__':
    main()
