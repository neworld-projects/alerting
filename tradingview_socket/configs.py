import json
import random
import string
from collections import ChainMap
from typing import List

import requests

from settings import AUTH_TOKEN, TRADINGVIEW_USERNAME


class InputDataFrame(object):
    def __init__(self, value):
        if value.get('isFake'):
            self.value = {
                value.get('id'): {
                    'v': value.get('defval'),
                    'f': value.get('isFake'),
                    't': value.get('type'),
                }
            }
        else:
            self.value = {
                value.get('id'): value.get('defval')
            }

    @property
    def __dict__(self):
        return self.value


class TradingViewConfig:
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "origin": "https://www.tradingview.com",
    }

    def __init__(self, timeframe: dict):
        self.timeframe = timeframe['name']
        self.cs_token = f'cs_{"".join(random.choices(string.ascii_letters + string.digits, k=12))}'
        self.qs_token = f'qs_{"".join(random.choices(string.ascii_letters + string.digits, k=12))}'

    @staticmethod
    def convert_to_str_send_message(message: dict) -> str:
        message = json.dumps(message).replace(" ", '')
        return f'~m~{message.__len__()}~m~{message}'

    @staticmethod
    def build_message(m: str, p: List) -> dict:
        return {"m": m, "p": p}

    @staticmethod
    def get_indicator(indicator_id: str, indicator_version: str):
        url = f'https://pine-facade.tradingview.com/pine-facade/translate/USER;{indicator_id}/{indicator_version}/?user_name={TRADINGVIEW_USERNAME}'
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'origin': 'https://www.tradingview.com',
            'referer': 'https://www.tradingview.com/'
        }
        response = requests.get(url, headers=headers).json()
        result = dict(
            ChainMap(*[
                {'text': response['result']['ilTemplate']},
                *[InputDataFrame(data).__dict__ for data in response['result']['metaInfo']['inputs'][::-1]]
            ])
        )
        result['pineVersion'] = indicator_version
        result['pineId'] = f'USER;{indicator_id}'
        return result

    def compile_message(self, m: str, p: List) -> str:
        return self.convert_to_str_send_message(self.build_message(m, p))

    @property
    def get_token_message(self) -> str:
        m = "set_auth_token"
        p = [AUTH_TOKEN, ]
        return self.compile_message(m, p)

    @property
    def get_chart_session_message(self) -> str:
        m = "chart_create_session"
        p = [self.cs_token, ""]
        return self.compile_message(m, p)

    @property
    def get_switch_timezone_message(self) -> str:
        m = "switch_timezone"
        p = [self.cs_token, "Etc/UTC"]
        return self.compile_message(m, p)

    @property
    def get_quote_session_message(self) -> str:
        m = "quote_create_session"
        p = [self.qs_token, ]
        return self.compile_message(m, p)

    def get_add_symbols_message(self, symbol) -> str:
        m = "quote_add_symbols"
        extra1 = {
            "adjustment": "splits",
            "currency-id": "XTVCUSDT",
            "session": "regular",
            "symbol": f"{symbol}"
        }
        p = [self.qs_token, f"={json.dumps(extra1)}"]
        return self.compile_message(m, p)

    def get_resolve_sample_chart_message(self, symbol, index) -> str:
        m = "resolve_symbol"
        extra1 = {
            "adjustment": "splits",
            "currency-id": "XTVCUSDT",
            "session": "regular",
            "symbol": f"{symbol}"
        }
        p = [self.cs_token, f'sds_sym_{index}', f"={json.dumps(extra1)}"]
        return self.compile_message(m, p)

    def get_create_series_message(self, length: int, index: int) -> str:
        m = "create_series"
        p = [self.cs_token, f"sds_{index}", f"s1", f"sds_sym_{index}", self.timeframe, length, ""]
        return self.compile_message(m, p)

    def get_more_data_message(self, length: int) -> str:
        m = "request_more_data"
        p = [self.cs_token, "sds_1", str(length)]
        return self.compile_message(m, p)

    def get_strategy_message(self, pine_id, pine_version, script_mode) -> str:
        m = 'create_study'
        p = [
            self.cs_token,
            'st7',
            'st1',
            'sds_1',
            'Script@tv-scripting-101!',
            self.get_indicator(pine_id, pine_version)
        ]
        return self.compile_message(m, p)
