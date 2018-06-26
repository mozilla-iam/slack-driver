from everett.manager import ConfigManager
from everett.manager import ConfigOSEnv

"""
:mod:`slack-driver.settings` -- Slack Driver Configuration
"""


def get_config():
    return ConfigManager(
        [
            ConfigOSEnv()
        ]
    )
