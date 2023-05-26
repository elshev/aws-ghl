from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import json
from typing import Iterable
from AwsSqsClient import AwsSqsClient
from AwsSsmClient import AwsSsmClient
from MgClient import MgClient
from AppConfig import AppConfig
from MgEvent import MgEvent
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_raw_events_from_url(url):
    mg_client = MgClient()
    result = mg_client.get_raw_events_from_url(url=url)
    return result


def get_raw_events(begin_date, end_date):
    mg_client = MgClient()
    result = mg_client.get_raw_events(begin_date=begin_date, end_date=end_date, limit=100)
    return result


def push_events_to_queue(raw_events: dict):
    if not raw_events:
        return False
    items = raw_events.get('items')
    if not items:
        logging.info('Raw Events do not contain "items". Nothing to send to SQS. raw_events:\n%s', raw_events)
        return False
    
    logging.info('Sending events to SQS Queue. Message Body:\n%s', items)
    sqs_client = AwsSqsClient()
    sqs_client.send_to_mailgun_events_queue(items)

    return True


def handler(event, context):
    """Gets events from MailGun and sends them to SQS

    Args:
        event (dict): handler parameters. Example:
        {
            "begin_date": "2023-05-19",
            "end_date": "2023-05-21"
        }
    """
    Util.log_lambda_event(event, context)

    begin_date = None
    end_date = None
    update_ssm_processed_datetime = True
    if event:
        begin_date_str = event.get('begin_date')
        if begin_date_str:
            begin_date = datetime.fromisoformat(begin_date_str)
            update_ssm_processed_datetime = False
        end_date_str = event.get('end_date')
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
            update_ssm_processed_datetime = False
        logging.info('Trying to get raw events from Mailgun. begin_date = %s, end_date = %s', begin_date, end_date)
    
    if not begin_date:
        begin_date = AwsSsmClient().get_mailgun_processed_datetime()
    if not end_date:
        end_date = begin_date + timedelta(days=1)
    if end_date > datetime.utcnow():
        end_date = datetime.utcnow()

    raw_events = get_raw_events(begin_date, end_date)
    
    while True:
        if not push_events_to_queue(raw_events=raw_events):
            break
        next_url = Util.get_dict_value(raw_events, ['paging', 'next'])
        if not next_url:
            break
        raw_events = get_raw_events_from_url(next_url)

    # Update last processed datetime in SSM if there were no begin or end dates passed into Lambda via 'event'
    if update_ssm_processed_datetime:
        logging.info('Setting "%s" SSM Parameter to = "%s"', AwsSsmClient.MAILGUN_PROCESSED_ISOTIME_PARAM_NAME, end_date)
        ssm_client = AwsSsmClient()
        ssm_client.set_mailgun_processed_datetime(end_date)