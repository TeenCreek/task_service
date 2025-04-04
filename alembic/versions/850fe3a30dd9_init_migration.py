"""init migration

Revision ID: 850fe3a30dd9
Revises: 
Create Date: 2025-04-04 08:16:22.243189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '850fe3a30dd9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('result', sa.Text(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    # ### end Alembic commands ###
