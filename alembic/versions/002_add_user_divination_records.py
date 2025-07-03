"""Add user_divination_records table

Revision ID: 002_add_user_divination_records
Revises: 001_initial_tables
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_user_divination_records'
down_revision = '001_initial_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 創建 user_divination_records 表
    op.create_table(
        'user_divination_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('divination_time', sa.DateTime(), nullable=False),
        sa.Column('week_start_date', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(1), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=True, default=121.5654),
        sa.Column('latitude', sa.Float(), nullable=True, default=25.0330),
        sa.Column('divination_result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('ix_user_divination_records_user_id', 'user_divination_records', ['user_id'])
    op.create_index('ix_user_divination_records_week_start_date', 'user_divination_records', ['week_start_date'])

def downgrade() -> None:
    op.drop_index('ix_user_divination_records_week_start_date', table_name='user_divination_records')
    op.drop_index('ix_user_divination_records_user_id', table_name='user_divination_records')
    op.drop_table('user_divination_records') 