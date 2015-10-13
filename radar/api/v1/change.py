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

from oslo_config import cfg
from pecan import expose
from pecan import response
from pecan import rest
from pecan.secure import secure
from wsme.exc import ClientSideError
import wsmeext.pecan as wsme_pecan
from wsme import types as wtypes

from radar.api.auth import authorization_checks as checks
from radar.api.v1.search import search_engine
from radar.api.v1 import wmodels
from radar.api.v1 import base
from radar.db.api import changes as changes_api
from lib2to3.fixer_util import String

CONF = cfg.CONF

SEARCH_ENGINE = search_engine.get_engine()


class Change(base.APIBase):
    """A model that describes a gerrit change.
    """

    change_id = wtypes.text
    """The gerrit change id.
    """
    project = wtypes.text
    subject = wtypes.text
    topic =  wtypes.text
    status = wtypes.text


class ChangesController(rest.RestController):
    """Manages operations on changes."""

    _custom_actions = {"search": ["GET"]}

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Change, int)
    def get_one_by_id(self, change_id):
        """Retrieve details about one change.

        :param change_id: An ID of the change.
        """
        change = changes_api.change_get(change_id)

        if change:
            return wmodels.Change.from_db_model(change)
        else:
            raise ClientSideError("Change %s not found" % change_id,
                                  status_code=404)


    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.Change], unicode, unicode, unicode, unicode,
                         unicode)
    def get(self, marker=None, limit=None, change_id=None, sort_field='id',
            sort_dir='asc'):
        """Retrieve definitions of all of the changes.

        :param name: A string to filter the name by.
        """

        # Boundary check on limit.
        if limit is None:
            limit = CONF.page_size_default
        limit = min(CONF.page_size_maximum, max(1, limit))

        # Resolve the marker record.
        marker_change = changes_api.change_get(marker)

        changes = changes_api \
            .change_get_all(marker=marker_change,
                           limit=limit,
                           change_id=change_id,
                           sort_field=sort_field,
                           sort_dir=sort_dir)
        change_count = changes_api \
            .change_get_count(change_id=change_id)

        # Apply the query response headers.
        response.headers['X-Limit'] = str(limit)
        response.headers['X-Total'] = str(change_count)
        if marker_change:
            response.headers['X-Marker'] = str(marker_change.id)

        if changes:
            return [wmodels.Change.from_db_model(c) for c in changes]
        else:
            raise ClientSideError("Could not retrieve changes list",
                                  status_code=404)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Change, unicode)
    def get_one_by_name(self, change_id):
        """Retrieve details about one change.

        :param change_id: The unique id of this change
        """
        change = changes_api.change_get_by_id(change_id)

        if change:
            return wmodels.Change.from_db_model(change)
        else:
            raise ClientSideError("Change %s not found" % change_id,
                                  status_code=404)


    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Change, unicode, body=wmodels.Change)
    def post(self, change_id, change):
        """Create a new change.

        :param change: a change within the request body.
        """
        change_dict = change.as_dict()

        created_change = changes_api.change_create(change_dict)

        return wmodels.Change.from_db_model(created_change)

    @secure(checks.guest)
    @wsme_pecan.wsexpose(wmodels.Change, int, body=wmodels.Change)
    def put(self, change_id, change):
        """Modify this change.

        :param change_id: An ID of the change.
        :param change: a change within the request body.
        """
        updated_change = changes_api.change_update(
            change_id,
            change.as_dict(omit_unset=True))

        if updated_change:
            return wmodels.Change.from_db_model(updated_change)
        else:
            raise ClientSideError("Change %s not found" % change_id,
                                  status_code=404)

    @secure(checks.superuser)
    @wsme_pecan.wsexpose(wmodels.Change, int)
    def delete(self, change_id):
        """Delete this change.

        :param change_id: An ID of the change.
        """
        changes_api.change_delete(change_id)

        response.status_code = 204


    def _is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @secure(checks.guest)
    @wsme_pecan.wsexpose([wmodels.Change], unicode, unicode, int, int)
    def search(self, q="", marker=None, limit=None):
        """The search endpoint for changes.

        :param q: The query string.
        :return: List of Changes matching the query.
        """

        changes = SEARCH_ENGINE.changes_query(q=q,
                                              marker=marker,
                                              limit=limit)

        return [wmodels.Change.from_db_model(change) for change in changes]

    @wsme_pecan.wsexpose(long, unicode)
    def count(self, kwargs):
        changes = changes_api.count()

        if changes:
            return changes
        else:
            raise ClientSideError("Cannot return change count for %s"
                                  % kwargs, status_code=404)

    @expose()
    def _route(self, args, request):
        if request.method == 'GET' and len(args) > 0:
            # It's a request by a name or id
            something = args[0]

            if something == "search":
                # Request to a search endpoint
                return super(ChangesController, self)._route(args, request)

            if self._is_int(something):
                # Get by id
                return self.get_one_by_id, args
            else:
                # Get by name
                if something == "count" and len(args) == 2:
                    return self.count, args
                else:
                    return self.get_one_by_name, ["/".join(args)]
        return super(ChangesController, self)._route(args, request)
