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

from oslo.config import cfg
from pecan import expose
from pecan import request
from pecan import response
from pecan import rest
from pecan.secure import secure
from wsme.exc import ClientSideError
import wsmeext.pecan as wsme_pecan

from radar.api.auth import authorization_checks as checks
from radar.api.v1.search import search_engine
from radar.api.v1 import wmodels
from radar.db.api import operators as operators_api
from radar.db.api import systems


CONF = cfg.CONF

SEARCH_ENGINE = search_engine.get_engine()


class OperatorsController(rest.RestController):
    """Manages operations on operators."""

    _custom_actions = {"search": ["GET"]}

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Operator, int)
    def get_one_by_id(self, operator_id):
        """Retrieve details about one operator.

        :param operator_id: An ID of the operator.
        """
        operator = operators_api.operator_get(operator_id)

        if operator:
            return wmodels.Operator.from_db_model(operator)
        else:
            raise ClientSideError("Operator %s not found" % operator_id,
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Operator, unicode)
    def get_one_by_name(self, operator_name):
        """Retrieve information about the given project.

        :param name: project name.
        """

        operator = operators_api.operator_get_by_name(operator_name)

        if operator:
            return wmodels.Operator.from_db_model(operator)
        else:
            raise ClientSideError("Operator %s not found" % operator_name,
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.Operator], int, int, unicode, unicode,
                         unicode)
    def get(self, marker=None, limit=None, operator_name=None, sort_field='id', 
            sort_dir='asc'):
        """Retrieve definitions of all of the operators.

        :param name: A string to filter the name by.
        """

        # Boundary check on limit.
        if limit is None:
            limit = CONF.page_size_default
        limit = min(CONF.page_size_maximum, max(1, limit))
 
        # Resolve the marker record.
        marker_operator = operators_api.operator_get(marker)
 
        operators = operators_api \
            .operator_get_all(marker=marker_operator,
                           limit=limit, 
                           name=operator_name,
                           sort_field=sort_field,
                           sort_dir=sort_dir)
        operator_count = operators_api \
            .operator_get_count(name=operator_name)
 
        # Apply the query response headers.
        response.headers['X-Limit'] = str(limit)
        response.headers['X-Total'] = str(operator_count)
        if marker_operator:
            response.headers['X-Marker'] = str(marker_operator.id)
 
        if operators:
            return [wmodels.Operator.from_db_model(o) for o in operators]
        else:
            raise ClientSideError("Could not retrieve operators list",
                                  status_code=404)


    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Operator, int, body=wmodels.Operator)
    def post(self, system_id, operator):
        """Create a new operator.

        :param operator: a operator within the request body.
        """
        operator_dict = operator.as_dict()

        created_operator = operators_api.operator_create(operator_dict)
        created_operator = operators_api.operator_add_system(created_operator.id, system_id)

        return wmodels.Operator.from_db_model(created_operator)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Operator, int, body=wmodels.Operator)
    def put(self, operator_id, operator):
        """Modify this operator.

        :param operator_id: An ID of the operator.
        :param operator: a operator within the request body.
        """
        updated_operator = operators_api.operator_update(
            operator_id,
            operator.as_dict(omit_unset=True))

        if updated_operator:
            return wmodels.Operator.from_db_model(updated_operator)
        else:
            raise ClientSideError("Operator %s not found" % operator_id,
                                  status_code=404)

    @secure(checks.superuser)
    @wsme_pecan.wsexpose(wmodels.Operator, int)
    def delete(self, operator_id):
        """Delete this operator.

        :param operator_id: An ID of the operator.
        """
        operators_api.operator_delete(operator_id)

        response.status_code = 204


    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.Operator], unicode, unicode, int, int)
    def search(self, q="", marker=None, limit=None):
        """The search endpoint for operators.

        :param q: The query string.
        :return: List of Operators matching the query.
        """

        operators = SEARCH_ENGINE.operators_query(q=q,
                                              marker=marker,
                                              limit=limit)

        return [wmodels.Operator.from_db_model(operator) for operator in operators]
    
    @wsme_pecan.wsexpose(long, unicode)
    def count(self, args):        
        operators = operators_api.count()
        
        if operators:
            return operators
        else:
            raise ClientSideError("Cannot return operator count for %s" 
                                  % kwargs, status_code=404)
            
    @expose()
    def _route(self, args, request):
        if request.method == 'GET' and len(args) > 0:
            # It's a request by a name or id
            something = args[0]

            if something == "search":
                # Request to a search endpoint
                return self.search, args
            
            if something == "count" and len(args) == 2:
                return self.count, args

            if self._is_int(something):
                # Get by id
                return self.get_one_by_id, args
            else:
                # Get by name
                return self.get_one_by_name, ["/".join(args)]

        return super(OperatorsController, self)._route(args, request)
