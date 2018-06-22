import json
import utils
import re

from settings import get_config
from vault import People

config = get_config()

custom_logger = utils.CISLogger(
    name=__name__,
    level=config('logging_level', namespace='cis', default='INFO'),
    cis_logging_output=config('logging_output', namespace='cis', default='cloudwatch'),
    cis_cloudwatch_log_group=config('cloudwatch_log_group', namespace='cis', default='staging')
).logger()

logger = custom_logger.get_logger()


def handle(event=None, context={}):
    logger.info('Initializing Slack driver.')

    logger.debug('Getting configuration from environment.')
    config = get_config()

    filter_prefix = config('prefix', namespace='slack_driver', default='mozilliansorg')
    driver_mode = config('interactive', namespace='slack_driver', default='True')
    environment = config('environment', namespace='slack_driver', default='development')

    logger.debug('Searching DynamoDb for people.')
    people = People()

    logger.debug('Filtering person list to groups.')
    groups = people.grouplist(filter_prefix)
    logger.debug('group list')
    logger.debug(str(groups))
