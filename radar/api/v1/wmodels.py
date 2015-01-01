from datetime import datetime
from wsme import types as wtypes
from radar.api.v1 import base

class System(base.APIBase):
    """Represents the ci systems for the dashboard
    """

    name = wtypes.text
    """The system name"""

class SystemEvent(base.APIBase):
    event_type = wtypes.text
    event_info = wtypes.text

class Operator(base.APIBase):
    operator_name = wtypes.text
    operator_email = wtypes.text

class User(base.APIBase):
    """Represents a user."""

    username = wtypes.text
    """A short unique name, beginning with a lower-case letter or number, and
    containing only letters, numbers, dots, hyphens, or plus signs"""

    full_name = wtypes.text
    """Full (Display) name."""

    openid = wtypes.text
    """The unique identifier, returned by an OpneId provider"""

    email = wtypes.text
    """Email Address."""

    is_superuser = bool

    last_login = datetime
    """Date of the last login."""

    enable_login = bool
    """Whether this user is permitted to log in."""

    @classmethod
    def sample(cls):
        return cls(
            username="elbarto",
            full_name="Bart Simpson",
            openid="https://login.launchpad.net/+id/Abacaba",
            email="skinnerstinks@springfield.net",
            is_staff=False,
            is_active=True,
            is_superuser=True,
            last_login=datetime(2014, 1, 1, 16, 42))


class AccessToken(base.APIBase):
    """Represents a user access token."""

    user_id = int
    """The ID of User to whom this token belongs."""

    access_token = wtypes.text
    """The access token."""

    expires_in = int
    """The number of seconds after creation when this token expires."""

    @classmethod
    def sample(cls):
        return cls(
            user_id=1,
            access_token="a_unique_access_token",
            expires_in=3600)
