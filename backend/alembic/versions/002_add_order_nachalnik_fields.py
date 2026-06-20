"""Add nachalnik fields to orders table

Revision ID: 002
Revises: 001
Create Date: 2026-06-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('nachalnik_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('orders', sa.Column('nachalnik_confirmed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'nachalnik_confirmed_at')
    op.drop_column('orders', 'nachalnik_id')
