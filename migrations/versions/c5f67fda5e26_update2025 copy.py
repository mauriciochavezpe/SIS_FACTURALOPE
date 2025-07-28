"""update2025 copy

Revision ID: c5f67fda5e26
Revises: 0fd5d7918b0a
Create Date: 2025-07-28 01:05:54.261837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5f67fda5e26'
down_revision = '0fd5d7918b0a'
branch_labels = None
depends_on = None


def upgrade():
     with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_type', sa.Integer(), nullable=True))
        


def downgrade():
    pass
