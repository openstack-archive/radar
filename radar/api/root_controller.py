from radar.api.v1.v1_controller import V1Controller
from pecan import expose
from pecan.core import redirect
class RootController(object):
    v1 = V1Controller()

