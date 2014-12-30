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

from oslo.db.sqlalchemy.utils import InvalidSortKey
from sqlalchemy.orm import subqueryload
from wsme.exc import ClientSideError

from radar.db.api import base as api_base
from radar.db import models


def system_get_by_id(system_id, session=None):
    return api_base.model_query(models.System, session) \
        .filter_by(id=system_id).first()

def count(session=None):
    return api_base.model_query(models.System, session) \
        .count()
        
def system_get_by_name(name, session=None):
    query = api_base.model_query(models.System, session)
    return query.filter_by(name=name).first()

def system_get_all(marker=None, limit=None, name=None, sort_field=None, 
                   sort_dir=None, **kwargs):
    # Sanity checks, in case someone accidentally explicitly passes in 'None'
    if not sort_field:
        sort_field = 'id'
    if not sort_dir:
        sort_dir = 'asc'

    query = _system_build_query(name=name, **kwargs)

    try:
        query = api_base.paginate_query(query=query,
                                        model=models.System,
                                        limit=limit,
                                        sort_keys=[sort_field],
                                        marker=marker,
                                        sort_dir=sort_dir)
    except InvalidSortKey:
        raise ClientSideError("Invalid sort_field [%s]" % (sort_field,),
                              status_code=400)
    except ValueError as ve:
        raise ClientSideError("%s" % (ve,), status_code=400)

    # Execute the query
    return query.all()

def system_create(values):
    return api_base.entity_create(models.System, values)

def system_update(system_id, values):
    return api_base.entity_update(models.System, system_id, values)

def system_delete(system_id):
    system = system_get(system_id)

    if system:
        api_base.entity_hard_delete(models.System, system_id)
        
def system_get_count(**kwargs):
    query = _system_build_query(**kwargs)
    
    return query.count()
        
def _system_build_query(**kwargs):
    query = api_base.model_query(models.System)
    query = api_base.apply_query_filters(query=query,
                                        model=models.System,
                                        **kwargs)

    return query
