import logging
import logging.config

logging.config.fileConfig('logging.conf')

#Create logger
logger = logging.getLogger('user-mgt-app')
