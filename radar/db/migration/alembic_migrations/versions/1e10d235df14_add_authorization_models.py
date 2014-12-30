"""add authorization models

Revision ID: 1e10d235df14
Revises: 135e9f8aeb9c
Create Date: 2014-12-19 05:16:31.019506

"""

# revision identifiers, used by Alembic.
revision = '1e10d235df14'
down_revision = '135e9f8aeb9c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

MYSQL_ENGINE = 'MyISAM'
MYSQL_CHARSET = 'utf8'

def upgrade(active_plugins=None, options=None):

    op.create_table(
        'authorization_codes',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Unicode(100), nullable=False),
        sa.Column('state', sa.Unicode(100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

    op.create_table(
        'accesstokens',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.Unicode(length=100), nullable=False),
        sa.Column('expires_in', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=MYSQL_CHARSET,
        mysql_engine=MYSQL_ENGINE)
    
    op.create_table(
        'refreshtokens',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.Unicode(length=100), nullable=False),
        sa.Column('expires_at', sa.DateTime(),nullable=False),
        sa.Column('expires_in', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=MYSQL_CHARSET,
        mysql_engine=MYSQL_ENGINE)


def downgrade(active_plugins=None, options=None):

    op.drop_table('refreshtokens')
    op.drop_table('accesstokens')
    op.drop_table('authorization_codes')