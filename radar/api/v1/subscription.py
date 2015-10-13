# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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
from pecan import abort
from pecan import request
from pecan import response
from pecan import rest
from pecan.secure import secure
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from radar.api.auth import authorization_checks as checks
from radar.api.v1 import base
from radar.db.api import subscriptions as subscription_api
from radar.db.api import users as user_api
from radar.openstack.common.gettextutils import _  # noqa


CONF = cfg.CONF


class Subscription(base.APIBase):
    """A model that describes a resource subscription.
    """

    user_id = int
    """The owner of this subscription.
    """

    target_type = wtypes.text
    """The type of resource that the user is subscribed to.
    """

    target_id = int
    """The database ID of the resource that the user is subscribed to.
    """

    @classmethod
    def sample(cls):
        return cls(
            user_id=1,
            target_type="subscription",
            target_id=1)


class SubscriptionsController(rest.RestController):
    """REST controller for Subscriptions.

    Provides Create, Delete, and search methods for resource subscriptions.
    """

    @secure(checks.authenticated)
    @wsme_pecan.wsexpose(Subscription, int)
    def get_one(self, subscription_id):
        """Retrieve a specific subscription record.

        :param subscription_id: The unique id of this subscription.
        """

        subscription = subscription_api.subscription_get(subscription_id)
        current_user = user_api.user_get(request.current_user_id)

        if subscription.user_id != request.current_user_id \
                and not current_user.is_superuser:
            abort(403, _("You do not have access to this record."))

        return Subscription.from_db_model(subscription)

    @secure(checks.authenticated)
    @wsme_pecan.wsexpose([Subscription], int, int, [unicode], int, int,
                         unicode, unicode)
    def get(self, marker=None, limit=None, target_type=None, target_id=None,
            user_id=None, sort_field='id', sort_dir='asc'):
        """Retrieve a list of subscriptions.

        :param marker: The resource id where the page should begin.
        :param limit: The number of subscriptions to retrieve.
        :param target_type: The type of resource to search by.
        :param target_id: The unique ID of the resource to search by.
        :param user_id: The unique ID of the user to search by.
        :param sort_field: The name of the field to sort on.
        :param sort_dir: sort direction for results (asc, desc).
        """

        # Boundary check on limit.
        if limit is None:
            limit = CONF.page_size_default
        limit = min(CONF.page_size_maximum, max(1, limit))

        # Sanity check on user_id
        current_user = user_api.user_get(request.current_user_id)
        if user_id != request.current_user_id \
                and not current_user.is_superuser:
            user_id = request.current_user_id

        # Resolve the marker record.
        marker_sub = subscription_api.subscription_get(marker)

        subscriptions = subscription_api.subscription_get_all(
            marker=marker_sub,
            limit=limit,
            target_type=target_type,
            target_id=target_id,
            user_id=user_id,
            sort_field=sort_field,
            sort_dir=sort_dir)
        subscription_count = subscription_api.subscription_get_count(
            target_type=target_type,
            target_id=target_id,
            user_id=user_id)

        # Apply the query response headers.
        response.headers['X-Limit'] = str(limit)
        response.headers['X-Total'] = str(subscription_count)
        if marker_sub:
            response.headers['X-Marker'] = str(marker_sub.id)

        return [Subscription.from_db_model(s) for s in subscriptions]

    @secure(checks.authenticated)
    @wsme_pecan.wsexpose(Subscription, body=Subscription)
    def post(self, subscription):
        """Create a new subscription.

        :param subscription: A subscription within the request body.
        """

        # Data sanity check - are all fields set?
        if not subscription.target_type or not subscription.target_id:
            abort(400, _('You are missing either the target_type or the'
                         ' target_id'))

        # Sanity check on user_id
        current_user = user_api.user_get(request.current_user_id)
        if not subscription.user_id:
            subscription.user_id = request.current_user_id
        elif subscription.user_id != request.current_user_id \
                and not current_user.is_superuser:
            abort(403, _("You can only subscribe to resources on your own."))

        # Data sanity check: The resource must exist.
        resource = subscription_api.subscription_get_resource(
            target_type=subscription.target_type,
            target_id=subscription.target_id)
        if not resource:
            abort(400, _('You cannot subscribe to a nonexistent resource.'))

        # Data sanity check: The subscription cannot be duplicated for this
        # user.
        existing = subscription_api.subscription_get_all(
            target_type=[subscription.target_type, ],
            target_id=subscription.target_id,
            user_id=subscription.user_id)

        if existing:
            abort(409, _('You are already subscribed to this resource.'))

        result = subscription_api.subscription_create(subscription.as_dict())
        return Subscription.from_db_model(result)

    @secure(checks.authenticated)
    @wsme_pecan.wsexpose(None, int)
    def delete(self, subscription_id):
        """Delete a specific subscription.

        :param subscription_id: The unique id of the subscription to delete.
        """
        subscription = subscription_api.subscription_get(subscription_id)

        # Sanity check on user_id
        current_user = user_api.user_get(request.current_user_id)
        if subscription.user_id != request.current_user_id \
                and not current_user.is_superuser:
            abort(403, _("You can only remove your own subscriptions."))

        subscription_api.subscription_delete(subscription_id)

        response.status_code = 204