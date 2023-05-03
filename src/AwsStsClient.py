import boto3


class AwsStsClient:

    def __init__(self) -> None:
        self._sts_client = boto3.client('sts')

    def get_aws_account_id(self):
        return self._sts_client.get_caller_identity()['Account']