"""add check constraint grade value non negative

Revision ID: b3c1d2e4f567
Revises: a91f2fe56f53
Create Date: 2026-05-06 00:04:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b3c1d2e4f567'
down_revision = 'a91f2fe56f53'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        'ck_grade_value_non_negative',
        'grades',
        'value >= 0'
    )


def downgrade():
    op.drop_constraint(
        'ck_grade_value_non_negative',
        'grades',
        type_='check'
    )
