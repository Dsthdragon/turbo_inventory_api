"""Create Stock

Revision ID: de9cbd217e6e
Revises: a9ca66a6aff6
Create Date: 2020-05-05 13:24:01.697625

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'de9cbd217e6e'
down_revision = 'a9ca66a6aff6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('catalog_id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['catalog_id'], ['catalog.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    #op.create_table('store_user',
    #sa.Column('store_id', sa.Integer(), nullable=True),
    #sa.Column('user_id', sa.Integer(), nullable=True),
    #sa.ForeignKeyConstraint(['store_id'], ['store.id'], ),
    #sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    #)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('store_user')
    op.drop_table('stock')
    # ### end Alembic commands ###
