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

from radar.common import exception as exc
from radar.db.api import base as api_base
from radar.db.api import systems
from radar.db import models


def change_get(change_id, session=None):
    return api_base.model_query(models.Change, session) \
        .filter_by(id=change_id).first()

def change_get_by_id(id, session=None):
    query = api_base.model_query(models.Change, session)
    return query.filter_by(change_id=id).first()

def count(session=None):
    return api_base.model_query(models.Change, session) \
        .count()
        
def change_get_all(marker=None, limit=None, name=None, sort_field=None, 
                   sort_dir=None, **kwargs):
    # Sanity checks, in case someone accidentally explicitly passes in 'None'
    if not sort_field:
        sort_field = 'id'
    if not sort_dir:
        sort_dir = 'asc'

    query = _change_build_query(name=name, **kwargs)

    try:
        query = api_base.paginate_query(query=query,
                                        model=models.Change,
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

def change_create(values):
    return api_base.entity_create(models.Change, values)
#

def change_update(change_id, values):
    return api_base.entity_update(models.Change, change_id, values)

def change_delete(change_id):
    change = change_get(change_id)

    if change:
        api_base.entity_hard_delete(models.Change, change_id)

def _entity_get(id, session=None):
    if not session:
        session = api_base.get_session()
    query = session.query(models.Change)\
        .filter_by(id=id)

    return query.first()

def change_get_count(**kwargs):
    query = _change_build_query(**kwargs)
    
    return query.count()

def _change_build_query(**kwargs):
    query = api_base.model_query(models.Change)
    query = api_base.apply_query_filters(query=query,
                                        model=models.Change,
                                        **kwargs)

    return query
