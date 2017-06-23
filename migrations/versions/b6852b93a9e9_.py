"""Initialize VPS Requests DB

Revision ID: b6852b93a9e9
Revises: 
Create Date: 2017-06-22 17:53:14.673046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6852b93a9e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vps_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Text(), nullable=True),
    sa.Column('request_project_size', sa.Text(), nullable=True),
    sa.Column('timeseries_has_response', sa.Boolean(), nullable=True),
    sa.Column('timeseries_response', sa.Text(), nullable=True),
    sa.Column('timeseries_interval_count', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vps_requests')
    # ### end Alembic commands ###