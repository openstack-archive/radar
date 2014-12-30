"""
SQLAlchemy Models
"""

from oslo.config import cfg
from oslo.db.sqlalchemy import models
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy import Enum
from sqlalchemy.ext import declarative
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import schema
from sqlalchemy import select
import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy_fulltext import FullText

import six.moves.urllib.parse as urlparse


CONF = cfg.CONF

def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database_connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.mysql_engine,
                'mysql_charset': "utf8"}
    return None

## CUSTOM TYPES

# A mysql medium text type.
MYSQL_MEDIUM_TEXT = UnicodeText().with_variant(MEDIUMTEXT(), 'mysql')


class IdMixin(object):
    id = Column(Integer, primary_key=True)


class RadarBase(models.TimestampMixin,
                    IdMixin,
                    models.ModelBase):
    metadata = None

    @declarative.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

Base = declarative.declarative_base(cls=RadarBase)

class ModelBuilder(object):
    def __init__(self, **kwargs):
        super(ModelBuilder, self).__init__()

        if kwargs:
            for key in kwargs:
                if key in self:
                    self[key] = kwargs[key]

class AuthorizationCode(ModelBuilder, Base):
    __tablename__ = "authorization_codes"
    code = Column(Unicode(100), nullable=False)
    state = Column(Unicode(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class AccessToken(ModelBuilder, Base):
    __tablename__ = "accesstokens"

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    access_token = Column(Unicode(100), nullable=False)
    expires_in = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class RefreshToken(ModelBuilder, Base):
    __tablename__ = "refreshtokens"

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    refresh_token = Column(Unicode(100), nullable=False)
    expires_in = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
user_permissions = Table(
    'user_permissions', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id')),
)

systems_operators = Table(
    'systems_operators', Base.metadata,
    Column('system_id', Integer, ForeignKey('systems.id')),
    Column('operator_id', Integer, ForeignKey('operators.id')),                       
)
class System(FullText, ModelBuilder, Base):
    __tablename__ = "systems"

    __fulltext_columns__ = ['name']

    name = Column(Unicode(50))
    events = relationship('SystemEvent', backref='system')
    operators = relationship("Operator", secondary="systems_operators")

    _public_fields = ["id", "name", "events", "operators"]


class SystemEvent(ModelBuilder, Base):
    __tablename__ = 'system_events'

    __fulltext_columns__ = ['event_type', 'event_info']

    system_id = Column(Integer, ForeignKey('systems.id'))
    event_type = Column(Unicode(100), nullable=False)
    event_info = Column(UnicodeText(), nullable=True)

    _public_fields = ["id", "system_id", "event_type", "event_info"]

class Operator(ModelBuilder, Base):
    __tablename__ = "operators"

    __fulltext_columns__ = ['operator_name', 'operator_email']

    operator_name = Column(Unicode(50))
    operator_email = Column(Unicode(50))
    systems = relationship('System', secondary="systems_operators")
    
    _public_fields = ["id", "operator_name", "operator_email", "systems"]

class User(FullText, ModelBuilder, Base):
    __table_args__ = (
        schema.UniqueConstraint('email', name='uniq_user_email'),
    )

    __fulltext_columns__ = ['username', 'full_name', 'email']

    username = Column(Unicode(30))
    full_name = Column(Unicode(255), nullable=True)
    email = Column(String(255))
    openid = Column(String(255))
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    permissions = relationship("Permission", secondary="user_permissions")
    enable_login = Column(Boolean, default=True)

    preferences = relationship("UserPreference")

    _public_fields = ["id", "openid", "full_name", "username", "last_login",
                      "enable_login"]

class Permission(ModelBuilder, Base):
    __table_args__ = (
        schema.UniqueConstraint('name', name='uniq_permission_name'),
    )
    name = Column(Unicode(50))
    codename = Column(Unicode(255))
    
class UserPreference(ModelBuilder, Base):
    __tablename__ = 'user_preferences'

    _TASK_TYPES = ('string', 'int', 'bool', 'float')

    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(Unicode(100))
    value = Column(Unicode(255))
    type = Column(Enum(*_TASK_TYPES), default='string')

    @property
    def cast_value(self):
        try:
            cast_func = {
                'float': lambda x: float(x),
                'int': lambda x: int(x),
                'bool': lambda x: bool(x),
                'string': lambda x: str(x)
            }[self.type]

            return cast_func(self.value)
        except ValueError:
            return self.value

    @cast_value.setter
    def cast_value(self, value):
        if isinstance(value, bool):
            self.type = 'bool'
        elif isinstance(value, int):
            self.type = 'int'
        elif isinstance(value, float):
            self.type = 'float'
        else:
            self.type = 'string'

        self.value = str(value)

    _public_fields = ["id", "key", "value", "type"]
    
class Subscription(ModelBuilder, Base):
    _SUBSCRIPTION_TARGETS = ('system')

    user_id = Column(Integer, ForeignKey('users.id'))
    target_type = Column(Enum(*_SUBSCRIPTION_TARGETS))

    # Cant use foreign key here as it depends on the type
    target_id = Column(Integer)

    _public_fields = ["id", "target_type", "target_id", "user_id"]
