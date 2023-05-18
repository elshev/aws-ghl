from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import json
from typing import Iterable
from MgClient import MgClient
from AppConfig import AppConfig
from MgEvent import MgEvent
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_raw_events(begin_date=None):
    if not begin_date:
        begin_date = datetime.utcnow().date() + timedelta(days=-1)
    end_date = datetime.utcnow().date() + timedelta(days=1)
 
    mg_client = MgClient()
    events = mg_client.get_raw_events(begin_date=begin_date, end_date=end_date, limit=100)

    return events


def push_events_to_queue(raw_events: dict):
    pass

def handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)

    events = get_raw_events()
    result = []
    for item in events['items']:
        mg_event = MgEvent.from_dict(item)
        # Exclude service events
        if mg_event.recipient.startswith('https://') or '/inbound_webhook' in mg_event.recipient:
            continue
        result.append(mg_event)
    
    return result
    