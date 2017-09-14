#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 01:38:57 2017

@author: romanromanenko
"""

# This script gets to bitstamp.net through their API and checks the balance
# of my account.

import requests
from pprint import pprint
from time import time
import hmac
import hashlib
import config

nonce = str(int(time()))
message = nonce + account_id + key

signature = hmac.new(
     bytearray(secret,'utf8'),
     msg=message.encode("UTF-8"),
     digestmod=hashlib.sha256).hexdigest().upper()

# getting daily stats
ticker_daily = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/").json()
bitstamp_output = {}

#reduce daily stats to only needed ones
for i in ticker_daily:
    if i in ('high', 'low', 'open', 'last'):
        bitstamp_output[i] = ticker_daily[i]

# getting my account balance
p = {"key" : key, 'signature': signature, 'nonce': nonce}
balance = requests.post("https://www.bitstamp.net/api/v2/balance/", data = p).json()

#reduce balance details to only needed ones
for i in balance:
    if i in ('btc_available', 'btc_balance', 'usd_available', 'usd_balance'):
        bitstamp_output[i] = balance[i]

pprint(bitstamp_output)
