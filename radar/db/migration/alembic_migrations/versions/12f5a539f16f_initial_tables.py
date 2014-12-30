"""initial_tables

Revision ID: 12f5a539f16f
Revises: 
Create Date: 2014-12-08 20:56:38.468330

"""

# revision identifiers, used by Alembic.
revision = '12f5a539f16f'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

MYSQL_ENGINE = 'MyISAM'
MYSQL_CHARSET = 'utf8'

def upgrade():
    
    op.create_table(
        'systems_operators',
        sa.Column('system_id', sa.Integer(), nullable=True),  
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['system_id'], ['systems.id'],),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ),
        sa.PrimaryKeyConstraint(),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET  
    )
    op.create_table(
        'systems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.UniqueConstraint('name', name='uniq_systems_name'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

    op.create_table(
        'system_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('event_type', sa.Unicode(length=100), nullable=False),
        sa.Column('event_info', sa.UnicodeText(), nullable=True),
        sa.Column('system_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET)

    op.create_table(
        'operators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('operator_name', sa.String(length=50), nullable=True),
        sa.Column('operator_email', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('operator_name', name='uniq_operator_name'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET)


def downgrade():
    op.drop_table('systems_operators')
    op.drop_table('systems')
    op.drop_table('system_events')
    op.drop_table('operators')
