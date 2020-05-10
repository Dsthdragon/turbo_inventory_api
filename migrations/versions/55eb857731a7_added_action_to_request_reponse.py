"""Added action To request reponse

Revision ID: 55eb857731a7
Revises: 57648523ca82
Create Date: 2020-05-07 11:50:42.815142

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '55eb857731a7'
down_revision = '57648523ca82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('request_response', sa.Column('action', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('request_response', 'action')
    # ### end Alembic commands ###