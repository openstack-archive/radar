from oslo.config import cfg

app = {
    'root': 'radar.api.root_controller.RootController',
    'modules': ['radar.api'],
    'debug': False
}

cfg.CONF.register_opts([
    cfg.IntOpt('page_size_maximum',
               default=500,
               help='The maximum number of results to allow a user to request '
                    'from the API'),
    cfg.IntOpt('page_size_default',
               default=20,
               help='The maximum number of results to allow a user to request '
                    'from the API')
])