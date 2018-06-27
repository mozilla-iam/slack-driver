import boto3
import logging

from boto3.dynamodb.conditions import Attr

try:
    from settings import get_config
except ImportError:
    from slack_driver.settings import get_config

logger = logging.getLogger(__name__)


class CISTable(object):
    def __init__(self, table_name):
        self.boto_session = boto3.session.Session()
        self.table_name = table_name
        self.table = None

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

    def people_in_group(self, groups):
        """Returns a list of dicts for each user that matches a group from the list"""
        found_users = []
        for user in self.table.all:
            logger.debug('processing user {}'.format(user))
            for user_glist in user.get('groups', []):
                if user_glist in groups:
                    found_users.append(user)
                    break

        logger.debug('Returning total of : {} users for this run of the connector.'.format(
            len(found_users))
        )
        return found_users
