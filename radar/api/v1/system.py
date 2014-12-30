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
from radar.db.api import systems as systems_api


CONF = cfg.CONF

SEARCH_ENGINE = search_engine.get_engine()


class SystemsController(rest.RestController):
    """Manages operations on systems."""

    _custom_actions = {"search": ["GET"],
                       "count": ["GET"]}

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.System, int)
    def get_one_by_id(self, system_id):
        """Retrieve details about one system.

        :param system_id: An ID of the system.
        """
        system = systems_api.system_get_by_id(system_id)

        if system:
            return wmodels.System.from_db_model(system)
        else:
            raise ClientSideError("System %s not found" % system_id,
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.System, unicode)
    def get_one_by_name(self, system_name):
        """Retrieve information about the given project.

        :param name: project name.
        """

        system = systems_api.system_get_by_name(system_name)

        if system:
            return wmodels.System.from_db_model(system)
        else:
            raise ClientSideError("System %s not found" % system_name,
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.System], int, int, unicode, unicode,
                         unicode)
    def get(self, marker=None, limit=None, name=None, sort_field='id', 
            sort_dir='asc'):
        """Retrieve definitions of all of the systems.
 
        :param name: A string to filter the name by.
        """
 
        # Boundary check on limit.
        if limit is None:
            limit = CONF.page_size_default
        limit = min(CONF.page_size_maximum, max(1, limit))
 
        # Resolve the marker record.
        marker_system = systems_api.system_get_by_id(marker)
 
        systems = systems_api \
            .system_get_all(marker=marker_system,
                           limit=limit, 
                           name=name,
                           sort_field=sort_field,
                           sort_dir=sort_dir)
        system_count = systems_api \
            .system_get_count(name=name)
 
        # Apply the query response headers.
        response.headers['X-Limit'] = str(limit)
        response.headers['X-Total'] = str(system_count)
        if marker_system:
            response.headers['X-Marker'] = str(marker_system.id)
 
        if systems:
            return [wmodels.System.from_db_model(s) for s in systems]
        else:
            raise ClientSideError("Could not retrieve system list",
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.System, body=wmodels.System)
    def post(self, system):
        """Create a new system.
        :param system: a system within the request body.
        """
        system_dict = system.as_dict()

        created_system = systems_api.system_create(system_dict)
        if created_system:
            return wmodels.System.from_db_model(created_system)
        else:
            raise ClientSideError("Unable to create system %s" % system,
                                  status_code=404)
        

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.System, int, body=wmodels.System)
    def put(self, system_id, system):
        """Modify this system.

        :param system_id: An ID of the system.
        :param system: a system within the request body.
        """
        updated_system = systems_api.system_update(
            system_id,
            system.as_dict(omit_unset=True))

        if updated_system:
            return wmodels.System.from_db_model(updated_system)
        else:
            raise ClientSideError("System %s not found" % system_id,
                                  status_code=404)

    @secure(checks.superuser)
    @wsme_pecan.wsexpose(wmodels.System, int)
    def delete(self, system_id):
        """Delete this system.

        :param system_id: An ID of the system.
        """
        systems_api.system_delete(system_id)

        response.status_code = 204


    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.System], unicode, int, int)
    def search(self, q="", marker=None, limit=None):
        """The search endpoint for systems.

        :param q: The query string.
        :return: List of Systems matching the query.
        """

        systems = SEARCH_ENGINE.systems_query(q=q,
                                              marker=marker,
                                              limit=limit)

        return [wmodels.System.from_db_model(system) for system in systems]
    
    
    @secure(checks.guest)
    @wsme_pecan.wsexpose(long, unicode)
    def count(self, args):        
        systems = systems_api.count()
        
        if systems:
            return systems
        else:
            raise ClientSideError("Cannot return system count for %s" 
                                  % kwargs, status_code=404)
    @expose()
    def _route(self, args, request):
        if request.method == 'GET' and len(args) > 0:
            # It's a request by a name or id
            something = args[0]

            if something == "search":
                # Request to a search endpoint
                return super(SystemsController, self)._route(args, request)
            
            if self._is_int(something):
                # Get by id
                return self.get_one_by_id, args
            else:
                # Get by name
                if something == "count" and len(args) == 2:
                    return self.count, args
                else:
                    return self.get_one_by_name, ["/".join(args)]
        return super(SystemsController, self)._route(args, request)
