import json
import utils
import requests
import yaml

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

def get_access_rules(appsyml):
    """
    Fetch access rules
    @appsyml str URL
    returns dict
    """
    ## Sample appsyml return value format:
    ## { 'apps': [
    ##            {'application': {'name': 'Account Portal', 'op': 'auth0', 'url': 'https://login.mozilla.com/', 'logo':
    ##            'accountmanager.png', 'authorized_users': [], 'authorized_groups': ['team_moco', 'team_mofo'],
    ##            'display': True, ## 'vanity_url': ['/accountmanager']}}
    ##           ]
    ## }
    logger.debug('Fetching access rules.')
    r = requests.get(appsyml)
    if not r.ok:
        logger.warning('Failed to fetch access rules, will not deprovision users.')
        return []

    access_rules = yaml.load(r.text).get('apps')
    logger.debug('Received apps.yml size {}'.format(len(r.text)))
    return access_rules

def handle(event=None, context={}):
    logger.info('Initializing Slack driver.')

    logger.debug('Getting configuration from environment.')
    config = get_config()

    filter_prefix = config('prefix', namespace='slack_driver', default='')
    driver_mode = config('interactive', namespace='slack_driver', default='True')
    environment = config('environment', namespace='slack_driver', default='development')
    appsyml = config('appsyml', namespace='slack_driver', default='https://cdn.sso.mozilla.com/apps.yml')
    slack_app = config('slack_app', namespace='slack_driver', default='Slack')


    access_rules = get_access_rules(appsyml)
    app = None
    authorized_groups = []
    for app in access_rules:
        actual_app = app.get('application')
        if actual_app.get('name') == slack_app:
            authorized_groups = actual_app.get('authorized_groups')
            logger.debug('Valid and authorized users are in groups {}'.format(authorized_groups))
            break

    if app == None:
        logger.warning('Did not find {} in access rules, will not deprovision users'.format(slack_app))
        return

    logger.debug('Searching DynamoDb for people.')
    people = People()

    logger.debug('Filtering person list to groups.')
    allowed_users = people.people_in_group(authorized_groups)
    logger.debug(str(allowed_users))
