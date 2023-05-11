import re
from typing import Any
from dataclasses import dataclass

@dataclass
class MgMessage:
    """ MailGun message """
    url: str
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
        _url = ''
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
        return MgMessage(
            url=_url,
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
            body_mime=_body_mime
        )
