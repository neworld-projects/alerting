#!/bin/bash

if [[ $(cat /etc/hostname) == telegram ]]; then
    python telegram_app.py
fi
if [[ $(cat /etc/hostname) == tradingview ]]; then
   python tradingview.py
fi