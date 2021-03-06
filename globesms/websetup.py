"""
PasteDeploy setup-app support for the globesms application.
"""

import logging
from paste.deploy import appconfig


log = logging.getLogger(__name__)


def setup_config(command, filename, section, vars):
    """
    Place any commands to setup the initial state of your application here.
    """
    # Load the application's config.
    conf = appconfig('config:'+filename, section.split(':',1)[1])

    log.info("setup_config is not configured. (see %s)" % __file__)

