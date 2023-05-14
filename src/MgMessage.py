import re
from typing import Any
from dataclasses import dataclass
from AppConfig import AppConfig

from MgEvent import MgEvent

@dataclass
class MgMessage:
    """ MailGun message """
    content_type: str
    feedback_id: str
    message_id: str
    mime_version: str
    reply_to: str
    subject: str
    to: str
    x_mailgun_variables: str
    sender: str
    recipients: str
    date: str
    body_mime: str
    mg_event: MgEvent


    @staticmethod
    def fix_body_mime(mime):

        """
        Workaround for MailGun bug: 'body-mime' contains mixed line endings '\n' and '\r\n'
        Replace single '\n' to '\r\n\' (but not '\n' in '\r\n')

        Args:
            mime (str): body_mime from MailGun response

        Returns:
            str: string with fixed line endings
        """
        
        if not mime:
            return mime
        pattern = '(?<!\\r)\\n'
        replacement = '\r\n'
        result = re.sub(pattern, replacement, mime)
        return result
    

    @staticmethod
    def from_dict(obj: Any) -> 'MgMessage':
        _content_type = str(obj.get("Content-Type"))
        _feedback_id = str(obj.get("Feedback-Id"))
        _message_id = str(obj.get("Message-Id"))
        _mime_version = str(obj.get("Mime-Version"))
        _reply_to = str(obj.get("Reply-To"))
        _subject = str(obj.get("Subject"))
        _to = str(obj.get("To"))
        _x_mailgun_variables = str(obj.get("X-Mailgun-Variables"))
        _sender = str(obj.get("sender"))
        _recipients = str(obj.get("recipients"))
        _date = str(obj.get("Date"))
        _body_mime = MgMessage.fix_body_mime(str(obj.get("body-mime")))
        _mg_event = None
        return MgMessage(
            content_type=_content_type,
            feedback_id=_feedback_id,
            message_id=_message_id,
            mime_version=_mime_version,
            reply_to=_reply_to,
            subject=_subject,
            to=_to,
            x_mailgun_variables=_x_mailgun_variables,
            sender=_sender,
            recipients=_recipients,
            date=_date,
            body_mime=_body_mime,
            mg_event=_mg_event
        )

    @property
    def key(self):
        return self.mg_event.message_key if self.mg_event else None
    
    @property
    def url(self):
        return self.mg_event.message_url if self.mg_event else None
    
    @property
    def location_id(self):
        return self.mg_event.location_id if self.mg_event else None

    @property
    def timestamp(self) -> float:
        return self.mg_event.timestamp if self.mg_event else None

    @property
    def recipient(self):
        return self.mg_event.recipient if self.mg_event else None

    @property
    def recipient_domain(self):
        return self.mg_event.recipient_domain if self.mg_event else None

    @property
    def is_reply_from_user(self):
        return self.recipient_domain == AppConfig.get_mailgun_domain()
