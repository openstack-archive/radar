"""add users permissions

Revision ID: 135e9f8aeb9c
Revises: 4d5b6d924547
Create Date: 2014-12-19 04:28:35.739935

"""

# revision identifiers, used by Alembic.
revision = '135e9f8aeb9c'
down_revision = '4d5b6d924547'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

MYSQL_ENGINE = 'MyISAM'
MYSQL_CHARSET = 'utf8'

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('username', sa.Unicode(length=30), nullable=True),
        sa.Column('full_name', sa.Unicode(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('openid', sa.String(length=255), nullable=True),
        sa.Column('is_staff', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('enable_login', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uniq_user_email'),
        sa.UniqueConstraint('username', name='uniq_user_username'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.Unicode(length=50), nullable=True),
        sa.Column('codename', sa.Unicode(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uniq_permission_name'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'user_permissions',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('permission_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint(),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

def downgrade():
    op.drop_table('users')
    op.drop_table('user_permissions')
    op.drop_table('permissions')
