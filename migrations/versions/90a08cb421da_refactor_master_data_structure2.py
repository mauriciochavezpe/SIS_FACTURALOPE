"""Refactor master_data structure2

Revision ID: 90a08cb421da
Revises: f275a7be56b4
Create Date: 2025-07-02 19:32:44.318702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90a08cb421da'
down_revision = 'f275a7be56b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_owner', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('full_name', sa.String(length=100), nullable=True))
        batch_op.alter_column('document_type',
               existing_type=sa.VARCHAR(length=1),
               type_=sa.String(length=2),
               existing_comment='Tipo de documento según SUNAT',
               existing_nullable=False)

    with op.batch_alter_table('master_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('catalog_code', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('code', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('value', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('status_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('extra', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('extra2', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('extra3', sa.String(length=255), nullable=True))
        batch_op.drop_constraint('master_data_data_value_key', type_='unique')
        batch_op.create_unique_constraint('uq_catalog_code_code', ['catalog_code', 'code'])
        batch_op.drop_column('description_value')
        batch_op.drop_column('id_status')
        batch_op.drop_column('data_value')
        batch_op.drop_column('description_table')
        batch_op.drop_column('code_table')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('master_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code_table', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('description_table', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('data_value', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('id_status', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('description_value', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.drop_constraint('uq_catalog_code_code', type_='unique')
        batch_op.create_unique_constraint('master_data_data_value_key', ['data_value'], postgresql_nulls_not_distinct=False)
        batch_op.drop_column('extra3')
        batch_op.drop_column('extra2')
        batch_op.drop_column('extra')
        batch_op.drop_column('status_id')
        batch_op.drop_column('description')
        batch_op.drop_column('value')
        batch_op.drop_column('code')
        batch_op.drop_column('catalog_code')

    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.alter_column('document_type',
               existing_type=sa.String(length=2),
               type_=sa.VARCHAR(length=1),
               existing_comment='Tipo de documento según SUNAT',
               existing_nullable=False)
        batch_op.drop_column('full_name')
        batch_op.drop_column('is_owner')

    # ### end Alembic commands ###
