"""Add missing tables for user preferences and time divination

Revision ID: 003_add_missing_tables
Revises: 002_add_user_divination_records
Create Date: 2025-01-06 22:47:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_missing_tables'
down_revision = '002_add_user_divination_records'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 創建 user_preferences 表
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('divination_gender', sa.String(1), nullable=True),
        sa.Column('location_longitude', sa.Float(), nullable=True, default=121.5654),
        sa.Column('location_latitude', sa.Float(), nullable=True, default=25.0330),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # 創建索引
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    
    # 創建 time_divination_history 表
    op.create_table(
        'time_divination_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_time', sa.DateTime(), nullable=False),
        sa.Column('current_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('gender', sa.String(1), nullable=False),
        sa.Column('purpose', sa.String(200), nullable=True),
        sa.Column('taichi_palace', sa.String(10), nullable=False),
        sa.Column('minute_dizhi', sa.String(2), nullable=False),
        sa.Column('sihua_results', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('ix_time_divination_history_user_id', 'time_divination_history', ['user_id'])
    op.create_index('ix_time_divination_history_target_time', 'time_divination_history', ['target_time'])
    
    # 創建 user_permissions 表
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, default='free'),
        sa.Column('subscription_status', sa.String(20), nullable=False, default='none'),
        sa.Column('subscription_start', sa.DateTime(), nullable=True),
        sa.Column('subscription_end', sa.DateTime(), nullable=True),
        sa.Column('subscription_price', sa.Float(), nullable=True, default=0.0),
        sa.Column('can_access_premium_features', sa.Boolean(), nullable=False, default=False),
        sa.Column('can_unlimited_divination', sa.Boolean(), nullable=False, default=False),
        sa.Column('can_access_admin_panel', sa.Boolean(), nullable=False, default=False),
        sa.Column('daily_api_calls', sa.Integer(), nullable=False, default=0),
        sa.Column('daily_api_limit', sa.Integer(), nullable=False, default=100),
        sa.Column('last_api_call_date', sa.DateTime(), nullable=True),
        sa.Column('registered_device_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_device_count', sa.Integer(), nullable=False, default=1),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # 創建索引
    op.create_index('ix_user_permissions_user_id', 'user_permissions', ['user_id'])
    
    # 創建 user_birth_info 表
    op.create_table(
        'user_birth_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('day', sa.Integer(), nullable=False),
        sa.Column('hour', sa.Integer(), nullable=False),
        sa.Column('minute', sa.Integer(), nullable=False, default=30),
        sa.Column('gender', sa.String(1), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=True, default=121.5654),
        sa.Column('latitude', sa.Float(), nullable=True, default=25.0330),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # 創建索引
    op.create_index('ix_user_birth_info_user_id', 'user_birth_info', ['user_id'])
    
    # 創建 user_devices 表
    op.create_table(
        'user_devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('device_fingerprint', sa.String(255), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('first_seen', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_seen', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('total_sessions', sa.Integer(), nullable=False, default=1),
        sa.Column('total_api_calls', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('ix_user_devices_user_id', 'user_devices', ['user_id'])
    
    # 創建 pending_bindings 表
    op.create_table(
        'pending_bindings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('birth_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.String(1), nullable=False, default='N'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('ix_pending_bindings_created_at', 'pending_bindings', ['created_at'])
    op.create_index('ix_pending_bindings_expires_at', 'pending_bindings', ['expires_at'])

def downgrade() -> None:
    op.drop_index('ix_pending_bindings_expires_at', table_name='pending_bindings')
    op.drop_index('ix_pending_bindings_created_at', table_name='pending_bindings')
    op.drop_table('pending_bindings')
    
    op.drop_index('ix_user_devices_user_id', table_name='user_devices')
    op.drop_table('user_devices')
    
    op.drop_index('ix_user_birth_info_user_id', table_name='user_birth_info')
    op.drop_table('user_birth_info')
    
    op.drop_index('ix_user_permissions_user_id', table_name='user_permissions')
    op.drop_table('user_permissions')
    
    op.drop_index('ix_time_divination_history_target_time', table_name='time_divination_history')
    op.drop_index('ix_time_divination_history_user_id', table_name='time_divination_history')
    op.drop_table('time_divination_history')
    
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences') 