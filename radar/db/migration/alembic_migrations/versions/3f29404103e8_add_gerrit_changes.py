"""add gerrit changes

Revision ID: 3f29404103e8
Revises: 842a5f411f2
Create Date: 2015-10-13 13:59:09.950867

"""

# revision identifiers, used by Alembic.
revision = '3f29404103e8'
down_revision = '842a5f411f2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

MYSQL_ENGINE = 'MyISAM'
MYSQL_CHARSET = 'utf8'

def upgrade():
    op.create_table(
        'gerrit_changes',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_id', sa.Unicode(length=50), nullable=False),
        sa.Column('project', sa.Unicode(length=50), nullable=False),
        sa.Column('subject', sa.Unicode(length=50), nullable=False),
        sa.Column('topic', sa.Unicode(length=50), nullable=False),
        sa.Column('status', sa.Unicode(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET);

    op.create_index('gerrit_changes_fti', 'gerrit_changes',
                    ['project', 'subject', 'topic'])


def downgrade():
    op.drop_index("gerrit_changes_fti", table_name='gerrit_changes')
    op.drop_table('gerrit_changes')
