"""add niche table

Revision ID: 23a14aaec65b
Revises: 61a1e5579038
Create Date: 2024-07-16 10:13:02.091087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '23a14aaec65b'
down_revision: Union[str, None] = '61a1e5579038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('niches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('niche', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('subniche', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('niches_keywords',
    sa.Column('niche_id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.ForeignKeyConstraint(['niche_id'], ['niches.id'], ),
    sa.PrimaryKeyConstraint('niche_id', 'keyword_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('niches_keywords')
    op.drop_table('niches')
    # ### end Alembic commands ###
