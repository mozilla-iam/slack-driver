"""Mozilla Slack Driver"""
import boto3
import credstash
import httplib2
import logging
import os
import time
import uuid

from settings import get_config


SA_CREDENTIALS_FILENAME = 'GDrive.json'
APPLICATION_NAME = 'Slack-Driver'

logger = logging.getLogger(__name__)


def get_secret(secret_name, context):
    """Fetch secret from environment or credstash."""
    secret = os.getenv(secret_name.split('.')[1], None)

    if not secret:
        secret = credstash.getSecret(
            name=secret_name,
            context=context,
            region="us-west-2"
        )
    return secret


class AuditTrail(object):
    def __init__(self):
        self.boto_session = boto3.session.Session()
        self.config = get_config()
        self.table_name = self.config('state_table', namespace='slack_driver', default='slack-driver-state')
        self.table = None

    def connect(self):
        resource = self.boto_session.resource('dynamodb')
        self.table = resource.Table(self.table_name)
        return self.table

    def create(self, drive):
        if self.table is None:
            self.connect()

        result = self.table.put_item(
            Item=drive
        )

        return result

    def is_blocked(self, drive_name):
        if self.table is None:
            self.connect()

        result = self.table.get_item(
            Key={
                'name': drive_name
            }
        )

        if result.get('Item', False):
            return True
        else:
            return False

    def populate(self, all_drive_objects):
        for drive in all_drive_objects:
            self.create(drive)

    def find(self, drive_name):
        if self.table is None:
            self.connect()

        result = self.table.get_item(
            Key={
                'name': drive_name
            }
        )

        return result.get('Item', False)

    def update(self, drive_name, members):
        if self.table is None:
            self.connect()

        result = self.table.get_item(
            Key={
                'name': drive_name
            }
        )

        item = result.get('Item', False)

        if item is not False:
            item['members'] = members
            result = self.table.put_item(
                Item=item
            )
        else:
            result = None

        return result


class SlackDriver(object):
        pass
