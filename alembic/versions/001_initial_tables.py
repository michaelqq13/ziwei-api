"""Initial database tables

Revision ID: 001_initial_tables
Revises: 
Create Date: 2024-12-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 創建 calendar_data 表
    op.create_table(
        'calendar_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('gregorian_datetime', sa.DateTime(), nullable=False),
        sa.Column('gregorian_year', sa.Integer(), nullable=False),
        sa.Column('gregorian_month', sa.Integer(), nullable=False),
        sa.Column('gregorian_day', sa.Integer(), nullable=False),
        sa.Column('gregorian_hour', sa.Integer(), nullable=False),
        sa.Column('lunar_year_in_chinese', sa.String(50), nullable=False),
        sa.Column('lunar_month_in_chinese', sa.String(50), nullable=False),
        sa.Column('lunar_day_in_chinese', sa.String(50), nullable=False),
        sa.Column('is_leap_month_in_chinese', sa.Boolean(), nullable=False),
        sa.Column('year_gan_zhi', sa.String(50), nullable=False),
        sa.Column('month_gan_zhi', sa.String(50), nullable=False),
        sa.Column('day_gan_zhi', sa.String(50), nullable=False),
        sa.Column('hour_gan_zhi', sa.String(50), nullable=False),
        sa.Column('minute_gan_zhi', sa.String(50), nullable=True),
        sa.Column('solar_term_today', sa.String(50), nullable=True),
        sa.Column('solar_term_in_hour', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_data_id'), 'calendar_data', ['id'], unique=False)
    
    # 創建 linebot_users 表
    op.create_table(
        'linebot_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('line_user_id', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('profile_picture_url', sa.String(length=1024), nullable=True),
        sa.Column('membership_level', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('line_user_id')
    )
    
    # 創建 divination_history 表
    op.create_table(
        'divination_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(length=1), nullable=False),
        sa.Column('divination_time', sa.DateTime(), nullable=False),
        sa.Column('taichi_palace', sa.String(length=50), nullable=False),
        sa.Column('minute_dizhi', sa.String(length=50), nullable=False),
        sa.Column('sihua_results', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['linebot_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建 chart_bindings 表
    op.create_table(
        'chart_bindings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('birth_year', sa.Integer(), nullable=False),
        sa.Column('birth_month', sa.Integer(), nullable=False),
        sa.Column('birth_day', sa.Integer(), nullable=False),
        sa.Column('birth_hour', sa.Integer(), nullable=False),
        sa.Column('birth_minute', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(length=1), nullable=False),
        sa.Column('calendar_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['linebot_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

def downgrade() -> None:
    op.drop_table('chart_bindings')
    op.drop_table('divination_history')
    op.drop_table('linebot_users')
    op.drop_index(op.f('ix_calendar_data_id'), table_name='calendar_data')
    op.drop_table('calendar_data') 