"""Added Transfer Status

Revision ID: 710cba898ad3
Revises: 4997304d0b15
Create Date: 2020-05-11 15:03:39.884635

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '710cba898ad3'
down_revision = '4997304d0b15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transfer_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_transfer_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], ),
    sa.ForeignKeyConstraint(['store_transfer_id'], ['store_transfer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('transfer_items')
    op.add_column('store_transfer', sa.Column('status', sa.String(length=255), nullable=False))
    op.drop_column('store_transfer', 'approved')
    op.drop_column('store_transfer', 'complete')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('store_transfer', sa.Column('complete', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('store_transfer', sa.Column('approved', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('store_transfer', 'status')
    op.create_table('transfer_items',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('stock_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('amount', mysql.FLOAT(), nullable=False),
    sa.Column('created', mysql.DATETIME(), nullable=True),
    sa.Column('updated', mysql.DATETIME(), nullable=True),
    sa.Column('store_transfer_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], name='transfer_items_ibfk_1'),
    sa.ForeignKeyConstraint(['store_transfer_id'], ['store_transfer.id'], name='transfer_items_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.drop_table('transfer_item')
    # ### end Alembic commands ###
