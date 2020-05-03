#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 01:38:57 2017

@author: romanromanenko
"""

# This script connects to bitstamp.net via their API and checks the balance of my account.

import json
import requests
from pprint import pprint
from time import time, ctime
import hmac
import hashlib
from bitstamp_config import *

#import for SMTP
import smtplib


def send_email(message):
    """ Send an email to details from config file with a passed message """

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
        message
        ])

    server.sendmail(from_email, to_email, msg)
    server.quit()

nonce = str(int(time()))
message = nonce + account_id + key

signature = hmac.new(
     bytearray(secret,'utf8'),
     msg=message.encode("UTF-8"),
     digestmod=hashlib.sha256).hexdigest().upper()

# getting daily stats
ticker_daily = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/").json()

# adding only needed daily general stats to the dictionary
bitstamp_output = { i : ticker_daily[i] for i in ticker_daily if i in ('high', 'low', 'open', 'last') }

# getting my account balance
payload = {"key" : key, 'signature': signature, 'nonce': nonce}
balance = requests.post("https://www.bitstamp.net/api/v2/balance/", data = payload).json()

# if there's an error, log this error
try:
    if balance['status'] == 'error':
        log_file = open("logfile.log", "a")
        log_file.write('\n\n'+ctime()+'\n')
        log_file.write(''+str(balance)+'\n\n')
        log_file.close()
except KeyError:
    # adding daily personal stats to the dictionary
    for i in balance:
        if i in ('btc_available', 'btc_balance', 'usd_available', 'usd_balance'):
            bitstamp_output[i] = balance[i]

#pprint(bitstamp_output)

# format resulted json, convert to str and send
send_email( str(json.dumps(bitstamp_output, sort_keys=True, indent=4)) )

