"""create subscriptions table

Revision ID: 842a5f411f2
Revises: 1e10d235df14
Create Date: 2014-12-19 21:41:15.172502

"""

# revision identifiers, used by Alembic.
revision = '842a5f411f2'
down_revision = '1e10d235df14'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

MYSQL_ENGINE = 'MyISAM'
MYSQL_CHARSET = 'utf8'

target_type_enum = sa.Enum('system', 'operator')

def upgrade():
    op.create_table(
        'subscriptions',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('target_type', target_type_enum, nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    op.drop_table('subscriptions')
