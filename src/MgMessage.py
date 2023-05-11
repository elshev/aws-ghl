import re
from typing import Any
from dataclasses import dataclass

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
        _body_mime = str(obj.get("body-mime"))
        _body_mime = MgMessage.fix_body_mime(_body_mime)
        return MgMessage(
            _content_type,
            _feedback_id,
            _message_id,
            _mime_version,
            _reply_to,
            _subject, _to,
            _x_mailgun_variables,
            _sender, _recipients,
            _body_mime)
