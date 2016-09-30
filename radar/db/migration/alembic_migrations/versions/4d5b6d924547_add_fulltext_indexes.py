#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""add fulltext indexes

Revision ID: 4d5b6d924547
Revises: 12f5a539f16f
Create Date: 2014-12-19 03:52:41.910419

"""

# revision identifiers, used by Alembic.
revision = '4d5b6d924547'
down_revision = '12f5a539f16f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE systems "
               "ADD FULLTEXT systems_name_fti (name)")

    op.execute("ALTER TABLE operators "
               "ADD FULLTEXT operators_fti (operator_name, operator_email)")

def downgrade():
    op.drop_index("systems_name_fti", table_name='systems')
    op.drop_index("operators_fti", table_name='operators')
