"""add minute_gan_zhi column

Revision ID: add_minute_gan_zhi_column
Revises: 
Create Date: 2024-05-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_minute_gan_zhi_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
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

def downgrade():
    # 刪除 calendar_data 表
    op.drop_index(op.f('ix_calendar_data_id'), table_name='calendar_data')
    op.drop_table('calendar_data') 