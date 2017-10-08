#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 02:45:39 2017

@author: romanromanenko
"""

# This script gets to bitstamp.net through their API and gets last 10 transactions
# Also it loads the date of the last transaction from the other file
# If there are transactions happened after the loaded date, it sends them out
# to the email and writes the new latest transaction date to the file
# Script is run once every hour by cron

#import for datetime operations
import datetime

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

nonce = str(int(time()))
message = nonce + account_id + key

signature = hmac.new(
     b'0KLRyMNqvGcjlso2aisnlxJPgqpdoKhW',
     msg=message.encode("UTF-8"),
     digestmod=hashlib.sha256).hexdigest().upper()

# get 10 last transactions in desc order
p = {"key" : key, 'signature': signature, 'nonce': nonce, 'offset':0, 'limit':10, 'sort':'desc'}
transaction_list = requests.post("https://www.bitstamp.net/api/v2/user_transactions/btcusd/", data = p).json()

# timepoint.txt file contains the date and time of the last transaction
# we open and read timepoint from that file
timepoint_file = open("timepoint.txt", "r")
timepoint_str = timepoint_file.readline().strip()
timepoint_dt = datetime.datetime.strptime(timepoint_str, '%Y-%m-%d %H:%M:%S')
timepoint_file.close()

# then we scan last 10 transactions and if they happened after timepoint, we save them
bitstamp_output = []
for i in range(len(transaction_list)):
    transaction = {}
    if datetime.datetime.strptime(transaction_list[i]['datetime'], '%Y-%m-%d %H:%M:%S') > timepoint_dt:
        for j in transaction_list[i]:
                if j in ('btc', 'btc_usd', 'datetime', 'fee', 'usd'):
                    transaction[j] = transaction_list[i][j]
        bitstamp_output += [transaction]
        
# if there was a transaction after the timepoint, we write its date and time to the file
if bitstamp_output:
    timepoint_file = open("timepoint.txt", "w")
    timepoint_file.write(transaction_list[0]['datetime'])
    timepoint_file.close()

    # format resulted json and convert to str before sending
    bitstamp_output_str = str(json.dumps(bitstamp_output, sort_keys=True, indent=4))

    # send an email with all details
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #server.ehlo()
    server.starttls()

    server.login(from_email, from_email_pass)

    msg = "\r\n".join([
            "From: " + from_email,
            "To: " + to_email,
            "Subject: BTC transactions today",
            "",
            bitstamp_output_str
            ])

    
    server.sendmail(from_email, to_email, msg)

    server.quit()