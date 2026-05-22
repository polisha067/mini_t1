"""Add is_reopened to contests

Revision ID: d1e2f3a4b5c6
Revises: 29be76f52d74
Create Date: 2026-05-22 17:14:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'c4d5e6f7a891'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('contests', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_reopened', sa.Boolean(), nullable=False, server_default='false')
        )


def downgrade():
    with op.batch_alter_table('contests', schema=None) as batch_op:
        batch_op.drop_column('is_reopened')
