"""empty message

Revision ID: 8ea91e12dc8b
Revises: 21cf839fce70
Create Date: 2020-04-27 20:17:18.880670

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8ea91e12dc8b'
down_revision = '21cf839fce70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Show', 'show_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('show_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###