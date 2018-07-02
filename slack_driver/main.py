import credstash
import json
import os
import utils
import requests
import slack
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

def verify_slack_users(config, allowed_users):
    """
    Find all Slack users which aren't allowed and deactivate them
    """
    # 1. list all slack users
    # 2. diff slack users with allowed_users
    # 3. disable all users in the diff and log

    slack_token = get_secret('slack-driver.token', {'app': 'slack-driver'}).split('\n')[0]
    sc = slack.SlackAPI(slack_token)

    slack_user_list = sc.get_users()
    logger.debug('Found {} Slack users in Slack database'.format(len(slack_user_list)))

    users = {}
    for user in slack_user_list:
        # Find primary email from the list of user's email
        user_email = None
        for e in user.get('emails'):
            if e.get('primary'):
                user_email = e.get('value')
                logger.debug('Found primary email {}'.format(user_email))
                break

        # Just in case Slack API somehow doesn't have a primary email. This should normally not happen.
        if user_email is None:
            user_email = user.get('emails')[0].get('value')
            logger.warning('No slack primary email set for user {}, '
                           'selecting first email in list {}'.format(e.get('id'), user_email))

        users[user_email] = user.get('id')

    logger.debug('allowed_users: {}'.format(allowed_users.keys()))
    logger.debug('users: {}'.format(users.keys()))
    users_to_disable = set(users.keys()) - set(allowed_users.keys())
    logger.debug('Will disable {} user(s) which should no longer have access to Slack'.format(len(users_to_disable)))

    for u in users_to_disable:
        logger.debug('Will now disable user {} ({})'.format(u, users[u]))
        #sc.deactivate_user(users[u])
    return True

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
            # XXX CIS with v1 profile prepend ldap groups with `ldap_` but the rest of the infra does not... so
            # workaround here:
            authorized_groups = []
            known_idp_prefix = ['mozilliansorg', 'hris', 'ldap']
            for g in actual_app.get('authorized_groups'):
                if g.split('_')[0] not in known_idp_prefix:
                    #its an ldap group
                    authorized_groups.append("ldap_"+g)
                else:
                    authorized_groups.append(g)

            logger.debug('Valid and authorized users are in groups {}'.format(authorized_groups))
            break

    if app == None:
        logger.warning('Did not find {} in access rules, will not deprovision users'.format(slack_app))
        return

    logger.debug('Searching DynamoDb for people.')
    people = People()

    logger.debug('Filtering person list to groups.')
    allowed_users = people.people_in_group(authorized_groups)
    logger.debug('Found {} Slack users which are allowed'.format(len(allowed_users)))

    logger.debug('Disable Slack users.')
    if not verify_slack_users(config, allowed_users):
        logger.warning('Failed to verify slack users will not deprovision users')
