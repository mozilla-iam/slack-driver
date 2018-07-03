import boto3
import logging
import utils

from boto3.dynamodb.conditions import Attr

try:
    from settings import get_config
except ImportError:
    from slack_driver.settings import get_config

def setup_logging():
    global logger
    config = get_config()
    custom_logger = utils.CISLogger(
        name=__name__,
        level=config('logging_level', namespace='cis', default='INFO'),
        cis_logging_output=config('logging_output', namespace='cis', default='cloudwatch'),
        cis_cloudwatch_log_group=config('cloudwatch_log_group', namespace='cis', default='staging')
    ).logger()

    logger = custom_logger.get_logger()

class CISTable(object):
    def __init__(self, table_name):
        self.boto_session = boto3.session.Session()
        self.table_name = table_name
        self.table = None
        setup_logging()

    def connect(self):
        resource = self.boto_session.resource('dynamodb')
        self.table = resource.Table(self.table_name)
        return self.table

    @property
    def all(self):
        if self.table is None:
            self.connect()

        response = self.table.scan(
                FilterExpression=Attr('active').eq(True)
            )

        users = response.get('Items')

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=Attr('active').eq(True),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            users.extend(response['Items'])

        logger.debug('Returning total: {} users from the identity vault.'.format(len(users)))
        return users


class People(object):
    def __init__(self):
        self.config = get_config()
        self.table_name = self.config('dynamodb_person_table', namespace='cis', default='fake-identity-vault')
        self.table = CISTable(self.table_name)
        setup_logging()

    def people_in_group(self, groups):
        """Returns a dict of dicts for each user that matches a group from the list"""
        found_users = {}
        for user in self.table.all:
            for user_glist in user.get('groups', []):
                if user_glist in groups:
                    found_users[user.get('primaryEmail')] = user
                    break

        logger.debug('Returning total of : {} users for this run of the connector.'.format(
            len(found_users))
        )
        return found_users
