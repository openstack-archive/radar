from radar.api import app
from oslo.config import cfg

CONF = cfg.CONF

CONF(project='radar')

application = app.setup_app()
