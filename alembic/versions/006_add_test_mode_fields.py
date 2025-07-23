"""add test mode fields to linebot users

Revision ID: 006_add_test_mode_fields
Revises: 005_add_taichi_palace_fields
Create Date: 2025-01-21 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_test_mode_fields'
down_revision = '005_add_taichi_palace_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add test mode fields to linebot_users table"""
    # Add test_role column
    op.add_column('linebot_users', sa.Column('test_role', sa.String(length=50), nullable=True))
    
    # Add test_expires_at column
    op.add_column('linebot_users', sa.Column('test_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove test mode fields from linebot_users table"""
    # Remove test_expires_at column
    op.drop_column('linebot_users', 'test_expires_at')
    
    # Remove test_role column
    op.drop_column('linebot_users', 'test_role') 