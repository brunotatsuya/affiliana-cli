"""initial schema

Revision ID: 61a1e5579038
Revises: 
Create Date: 2024-07-14 21:21:15.231933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '61a1e5579038'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('keywords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('language', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('loc_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('PRIMARY', 'SUGGESTION', 'MATCH', name='keywordtypeenum'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('metrics_reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.Column('competition', sa.Float(), nullable=False),
    sa.Column('volume', sa.Integer(), nullable=False),
    sa.Column('cpc', sa.Float(), nullable=False),
    sa.Column('cpc_dollars', sa.Float(), nullable=False),
    sa.Column('sd', sa.Integer(), nullable=False),
    sa.Column('pd', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('serp_analyses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('suggestion_sets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('serp_analysis_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serp_analysis_id', sa.Integer(), nullable=False),
    sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('domain', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('clicks', sa.Integer(), nullable=True),
    sa.Column('domain_authority', sa.Integer(), nullable=True),
    sa.Column('facebook_shares', sa.Integer(), nullable=True),
    sa.Column('pinterest_shares', sa.Integer(), nullable=True),
    sa.Column('linkedin_shares', sa.Integer(), nullable=True),
    sa.Column('google_shares', sa.Integer(), nullable=True),
    sa.Column('reddit_shares', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['serp_analysis_id'], ['serp_analyses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('suggestion_sets_keywords',
    sa.Column('suggestion_set_id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.ForeignKeyConstraint(['suggestion_set_id'], ['suggestion_sets.id'], ),
    sa.PrimaryKeyConstraint('suggestion_set_id', 'keyword_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('suggestion_sets_keywords')
    op.drop_table('serp_analysis_items')
    op.drop_table('suggestion_sets')
    op.drop_table('serp_analyses')
    op.drop_table('metrics_reports')
    op.drop_table('keywords')
    # ### end Alembic commands ###
