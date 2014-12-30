# Copyright (c) 2014 Triniplex.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from oslo.config import cfg
from pika.exceptions import ConnectionClosed
from stevedore import enabled

from radar.openstack.common import log
from radar.worker.task.process_update import ProcessCISystems


CONF = cfg.CONF
LOG = log.getLogger(__name__)


def update():
    log.setup('radar')
    CONF(project='radar')

    updater = Updater()
    updater.start()

    while updater.started:
        LOG.info("processing systems")
        updater.systems.do_update()
        LOG.info("done processing systems. Sleeping for 5 minutes.")

        time.sleep(300)
        continue

class Updater():
    def __init__(self):
        self.started = False
        self.systems = ProcessCISystems()

    def start(self):
        self.started = True
        
    def stop(self):
        self.started = False
