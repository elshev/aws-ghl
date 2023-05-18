from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import json
from typing import Iterable
from AwsS3Client import AwsS3Client
from MgClient import MgClient
from AppConfig import AppConfig
from MgMessage import MgMessage
from Util import Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_messages_mime(begin_date=None) -> Iterable[MgMessage]:
    if not begin_date:
        begin_date = datetime.utcnow().date() + timedelta(days=-1)
    end_date = datetime.utcnow().date() + timedelta(days=1)
 
    mg_client = MgClient()
    messages = mg_client.get_messages_mime(begin_date=begin_date, end_date=end_date)
    # messages_json = json.dumps(messages, indent=2)
    # logging.debug(messages_json)

    return messages


def handler(event, context):
    logger.info('Event: %s', event)
    if not context is None:
        logger.info('Context: %s', context)

    messages = get_messages_mime()

    s3_client = AwsS3Client()
    for message in messages:
        s3_client.upload_message_to_s3(message)
