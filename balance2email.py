#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 22:22:00 2017

@author: romanromanenko
"""
# This script gets to bitstamp.net through their API and checks the balance
# of my account, then sends it to me.
# Script is run once a day by cron


#import for API
import json
import requests
from pprint import pprint
from time import time
import hmac
import hashlib
from bitstamp_config import *

#import for SMTP
import smtplib

# API details in config file

nonce = str(int(time()))
message = nonce + account_id + key

signature = hmac.new(
     b'0KLRyMNqvGcjlso2aisnlxJPgqpdoKhW',
     msg=message.encode("UTF-8"),
     digestmod=hashlib.sha256).hexdigest().upper()

# getting daily stats
ticker_daily = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/").json()
bitstamp_output = {}

#reduce daily stats to only needed ones
for i in ticker_daily:
    if i in ('high', 'low', 'open', 'last'):
        bitstamp_output[i] = ticker_daily[i]

# getting my personal balance
p = {"key" : key, 'signature': signature, 'nonce': nonce}
balance = requests.post("https://www.bitstamp.net/api/v2/balance/", data = p).json()

# reduce balance details to only needed ones and add to the total dictionary with values
for i in balance:
    if i in ('btc_available', 'btc_balance', 'usd_available', 'usd_balance'):
        bitstamp_output[i] = balance[i]

# format resulted json and convert to str before sending
bitstamp_output_str = str(json.dumps(bitstamp_output, sort_keys=True, indent=4))

# send an email with all details
server = smtplib.SMTP('smtp.gmail.com', 587)
#server.ehlo()
server.starttls()

# Email details in config file

server.login(from_email, from_email_pass)

msg = "\r\n".join([
  "From: " + from_email,
  "To: " + to_email,
  "Subject: BTC today",
  "",
  bitstamp_output_str
  ])

server.sendmail(from_email, to_email, msg)

server.quit()