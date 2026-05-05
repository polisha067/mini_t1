"""add reset token fields to users

Revision ID: c4d5e6f7a891
Revises: b3c1d2e4f567
Create Date: 2026-05-06 01:11:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d5e6f7a891'
down_revision = 'b3c1d2e4f567'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token_hash', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expires', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_users_reset_token_hash', ['reset_token_hash'], unique=False)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_reset_token_hash')
        batch_op.drop_column('reset_token_expires')
        batch_op.drop_column('reset_token_hash')
