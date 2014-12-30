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


def operator_get(operator_id, session=None):
    return api_base.model_query(models.Operator, session) \
        .filter_by(id=operator_id).first()

def operator_get_by_name(name, session=None):
    query = api_base.model_query(models.Operator, session)
    return query.filter_by(operator_name=name).first()

def count(session=None):
    return api_base.model_query(models.Operator, session) \
        .count()
        
def operator_get_all(marker=None, limit=None, name=None, sort_field=None, 
                   sort_dir=None, **kwargs):
    # Sanity checks, in case someone accidentally explicitly passes in 'None'
    if not sort_field:
        sort_field = 'id'
    if not sort_dir:
        sort_dir = 'asc'

    query = _operator_build_query(name=name, **kwargs)

    try:
        query = api_base.paginate_query(query=query,
                                        model=models.Operator,
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

def operator_create(values):
    return api_base.entity_create(models.Operator, values)

def operator_add_system(operator_id, system_id):
    session = api_base.get_session()
    
    with session.begin():
        operator = _entity_get(operator_id, session)
        if operator is None:
            raise exc.NotFound("%s %s not found"
                               % ("Operator", operator_id))

        system = systems.system_get_by_id(system_id, session)
        if system is None:
            raise exc.NotFound("%s %s not found"
                               % ("System", system_id))

        if system_id in [s.id for s in operator.systems]:
            raise ClientSideError("The System %d is already associated with"
                                  "Operator %d" %
                                  (system_id, operator_id))

        operator.systems.append(system)
        session.add(operator)
        return operator

def operator_update(operator_id, values):
    return api_base.entity_update(models.Operator, operator_id, values)

def operator_delete(operator_id):
    operator = operator_get(operator_id)

    if operator:
        api_base.entity_hard_delete(models.Operator, operator_id)

def _entity_get(id, session=None):
    if not session:
        session = api_base.get_session()
    query = session.query(models.Operator)\
        .filter_by(id=id)

    return query.first()

def operator_get_count(**kwargs):
    query = _operator_build_query(**kwargs)
    
    return query.count()

def _operator_build_query(**kwargs):
    query = api_base.model_query(models.Operator)
    query = api_base.apply_query_filters(query=query,
                                        model=models.Operator,
                                        **kwargs)

    return query
