import logging
import logging.config
import os
import json
import structlog
from datetime import datetime
from pythonjsonlogger import jsonlogger

config_path = os.path.join(os.path.dirname(__file__), '..', 'logging.conf')
logging.config.fileConfig(config_path, disable_existing_loggers=False)

# Configure structlog for structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create structured logger
app_logger = structlog.get_logger('appLogger')

# Create a custom JSON formatter for file logging
class CustomJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.utcnow().isoformat()
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        if not log_record.get('service'):
            log_record['service'] = 'user-mgt-api'
        if not log_record.get('environment'):
            log_record['environment'] = 'development'

# Configure file handler with JSON formatter
file_handler = logging.FileHandler('app_events.log')
file_handler.setFormatter(CustomJSONFormatter())

# Get the app logger and add the JSON file handler
logger = logging.getLogger('appLogger')
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
