"""Updates

Revision ID: b2de95284f0f
Revises: fb6978d359a2
Create Date: 2020-04-25 19:03:17.285920

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'b2de95284f0f'
down_revision = 'fb6978d359a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('other', sa.Column('blocked', sa.Boolean(), nullable=True))
    op.add_column('request', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('blocked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'blocked')
    op.drop_column('request', 'comment')
    op.drop_column('other', 'blocked')
    # ### end Alembic commands ###
