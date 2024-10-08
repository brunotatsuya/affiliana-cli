"""Add is_sponsored column to amazon_products table

Revision ID: 7c70dfd4c4e4
Revises: fdc1e771cd13
Create Date: 2024-08-17 18:18:29.055535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7c70dfd4c4e4'
down_revision: Union[str, None] = 'fdc1e771cd13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('amazon_products', sa.Column('is_sponsored', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('amazon_products', 'is_sponsored')
    # ### end Alembic commands ###
