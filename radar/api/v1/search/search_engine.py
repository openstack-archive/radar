# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc

from oslo.config import cfg

from radar.db import models

CONF = cfg.CONF

SEARCH_OPTS = [
    cfg.StrOpt('search_engine',
               default='sqlalchemy',
               help='Search engine implementation.'
                    ' The only supported type is "sqlalchemy".')
]

CONF.register_opts(SEARCH_OPTS)


class SearchEngine(object):
    """This is an interface that should be implemented by search engines.

    """

    searchable_fields = {
        models.System: ["name"],
        models.Operator: ["operator_name", "operator_email"],
        models.SystemEvent: ["event_type", "event_info"],
    }

    @abc.abstractmethod
    def systems_query(self, q, name=None,
                      marker=None, limit=None, **kwargs):
        pass

ENGINE = None


def get_engine():
    global ENGINE
    return ENGINE


def set_engine(impl):
    global ENGINE
    ENGINE = impl
