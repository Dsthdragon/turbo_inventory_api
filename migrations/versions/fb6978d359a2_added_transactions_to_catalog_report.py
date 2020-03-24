"""Added transactions to Catalog Report

Revision ID: fb6978d359a2
Revises: cdaf5e9e9793
Create Date: 2020-03-24 10:04:56.005770

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'fb6978d359a2'
down_revision = 'cdaf5e9e9793'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('catalog_report', sa.Column('transactions', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('catalog_report', 'transactions')
    # ### end Alembic commands ###
