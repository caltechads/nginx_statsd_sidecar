import logging
import sys

from pythonjsonlogger import jsonlogger


root = logging.getLogger()
root.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
root.addHandler(logHandler)

logger = logging.getLogger('nginx_statsd_sidecar')
