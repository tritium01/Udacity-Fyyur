"""empty message

Revision ID: 874277a72650
Revises: 8ea91e12dc8b
Create Date: 2020-04-29 21:57:17.555271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '874277a72650'
down_revision = '8ea91e12dc8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###