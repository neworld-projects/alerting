import _thread
import logging
import re
from json import loads
from typing import List

import websocket

from settings import TRADINGVIEW_WEBSOCKET_URL
from tradingview_socket.configs import TradingViewConfig

logging.DEBUG = False


class OpenWebsocketConnection:
    def __init__(self, symbols: List, timeframe: dict):
        self.symbols = symbols
        self.timeframe = timeframe
        self.config = TradingViewConfig(timeframe)
        websocket.enableTrace(True)
        self.coin_map = {}
        self.ws_app = websocket.WebSocketApp(
            url=TRADINGVIEW_WEBSOCKET_URL,
            header=self.config.headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, ws, message):
        if re.search("~m~[0-9]+~m~~h~[0-9]+", message):
            ws.send(message)
            return None
        else:
            split_message = re.split("~m~[0-9]+~m~", message)
            list_json_message = []
            for convert in split_message[1:]:
                try:
                    list_json_message.append(loads(convert))
                except Exception as e:
                    logging.error(e)
            return list_json_message

    def on_error(self, ws, error):
        logging.error(error, extra={'info': {"timeframe": self.timeframe}})

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning('close', extra={'info': {"timeframe": self.timeframe}})

    def on_open(self, ws):
        def run_basic(index_, symbol_):
            config = TradingViewConfig(self.timeframe)

            ws.send(config.get_token_message)

            ws.send(config.get_chart_session_message)

            ws.send(config.get_switch_timezone_message)

            ws.send(config.get_quote_session_message)

            ws.send(config.get_add_symbols_message(symbol_))

            ws.send(config.get_resolve_sample_chart_message(symbol_, index_))

            ws.send(config.get_create_series_message(300, index_))

        def run_another(index_, symbol_):
            config = TradingViewConfig(self.timeframe)

            ws.send(config.get_chart_session_message)

            ws.send(config.get_switch_timezone_message)

            ws.send(config.get_resolve_sample_chart_message(symbol_, index_))

            ws.send(config.get_create_series_message(300, index_))

        for index, symbol in enumerate(self.symbols, start=1):
            self.coin_map[f'sds_{index}'] = symbol
            if index == 1:
                _thread.start_new_thread(run_basic, (index, symbol))
            else:
                _thread.start_new_thread(run_another, (index, symbol))
