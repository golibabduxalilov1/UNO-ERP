"""Initial migration - all tables

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('login', sa.String(100), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('admin','brigadir','nachalnik','operator','cutter','driller','driver','director', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.UniqueConstraint('login'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])

    # Clients
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
    )
    op.create_index('ix_clients_id', 'clients', ['id'])
    op.create_index('ix_clients_phone', 'clients', ['phone'])

    # Orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.String(20), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('new','cutting','drilling','assembling','pending_nachalnik','ready','delivered','cancelled', name='orderstatus'), nullable=False),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('nachalnik_id', sa.Integer(), nullable=True),
        sa.Column('nachalnik_confirmed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['nachalnik_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_order_no', 'orders', ['order_no'])
    op.create_index('ix_orders_client_id', 'orders', ['client_id'])
    op.create_index('ix_orders_created_by', 'orders', ['created_by'])

    # Order Details
    op.create_table(
        'order_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('furniture_type', sa.String(100), nullable=False),
        sa.Column('height_mm', sa.Integer(), nullable=False),
        sa.Column('width_mm', sa.Integer(), nullable=False),
        sa.Column('depth_mm', sa.Integer(), nullable=False),
        sa.Column('holes', sa.Text(), nullable=True),
        sa.Column('cuts', sa.Text(), nullable=True),
        sa.Column('material', sa.String(100), nullable=False),
        sa.Column('color', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
    )
    op.create_index('ix_order_details_id', 'order_details', ['id'])
    op.create_index('ix_order_details_order_id', 'order_details', ['order_id'])

    # Order Stages
    op.create_table(
        'order_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.Enum('cutting','drilling','assembling', name='stagetype'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('in_progress','pending_brigadir','confirmed','rejected', name='stagestatus'), nullable=False),
        sa.Column('brigadir_id', sa.Integer(), nullable=True),
        sa.Column('brigadir_confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('brigadir_reject_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['brigadir_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_order_stages_id', 'order_stages', ['id'])
    op.create_index('ix_order_stages_order_id', 'order_stages', ['order_id'])
    op.create_index('ix_order_stages_user_id', 'order_stages', ['user_id'])
    op.create_index('ix_order_stages_brigadir_id', 'order_stages', ['brigadir_id'])

    # Deliveries
    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
    )
    op.create_index('ix_deliveries_id', 'deliveries', ['id'])
    op.create_index('ix_deliveries_order_id', 'deliveries', ['order_id'])
    op.create_index('ix_deliveries_driver_id', 'deliveries', ['driver_id'])

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('deliveries')
    op.drop_table('order_stages')
    op.drop_table('order_details')
    op.drop_table('orders')
    op.drop_table('clients')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS stagetype")
    op.execute("DROP TYPE IF EXISTS stagestatus")
