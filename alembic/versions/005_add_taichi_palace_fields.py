"""Add taichi palace mapping and chart data fields to divination_history

Revision ID: 005_add_taichi_palace_fields
Revises: 004_add_is_active_to_linebotuser
Create Date: 2025-01-06 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_taichi_palace_fields'
down_revision = '004_add_is_active_to_linebotuser'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 添加新字段到 divination_history 表
    op.add_column('divination_history', sa.Column('taichi_palace_mapping', sa.Text(), nullable=True))
    op.add_column('divination_history', sa.Column('taichi_chart_data', sa.Text(), nullable=True))

def downgrade() -> None:
    # 移除字段
    op.drop_column('divination_history', 'taichi_chart_data')
    op.drop_column('divination_history', 'taichi_palace_mapping') 