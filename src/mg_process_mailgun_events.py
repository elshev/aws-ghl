from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import json
from typing import Iterable
from AwsSqsClient import AwsSqsClient
from MgClient import MgClient
from AppConfig import AppConfig
from MgEvent import MgEvent
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_raw_events(url=None, begin_date=None):
    mg_client = MgClient()
    result = {}
    if (url):
        result = mg_client.get_raw_events_from_url(url=url)
    else:
        if not begin_date:
            begin_date = datetime.utcnow().date() + timedelta(days=-1)
        end_date = datetime.utcnow().date() + timedelta(days=1)

        result = mg_client.get_raw_events(begin_date=begin_date, end_date=end_date, limit=100)

    return result


def push_events_to_queue(raw_events: dict):
    if not raw_events:
        return False
    items = raw_events.get('items')
    if not items:
        return False
    
    sqs_client = AwsSqsClient()
    sqs_client.send_to_mailgun_events_queue(items)

    return True


def handler(event, context):
    Util.log_lambda_event(event, context)

    raw_events = get_raw_events()
    
    while True:
        if not push_events_to_queue(raw_events=raw_events):
            break
        next_url = Util.get_dict_value(raw_events, ['paging', 'next'])
        if not next_url:
            break
        raw_events = get_raw_events(next_url)
