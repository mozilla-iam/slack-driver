from everett.manager import ConfigManager
from everett.manager import ConfigOSEnv

"""
:mod:`slack-driver.settings` -- GSuite Driver Configuration
* Environment variables used
* SLACK_DRIVER_PREFIX
"""


def get_config():
    return ConfigManager(
        [
            ConfigOSEnv()
        ]
    )
