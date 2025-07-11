"""Create initial tables

Revision ID: 0b2a1d619939
Revises: 
Create Date: 2025-07-02 19:33:43.986540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2a1d619939'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('priority', sa.Enum('CRITICAL', 'HIGH', 'NORMAL', 'LOW', name='prioritylevel'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED', 'BLOCKED', name='jobstatus'), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=True),
    sa.Column('resource_requirements', sa.JSON(), nullable=True),
    sa.Column('retry_config', sa.JSON(), nullable=True),
    sa.Column('timeout_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_job_id'), 'jobs', ['job_id'], unique=True)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
    op.create_index(op.f('ix_jobs_type'), 'jobs', ['type'], unique=False)
    op.create_table('job_dependencies',
    sa.Column('job_id', sa.Integer(), nullable=False),
    sa.Column('depends_on_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['depends_on_id'], ['jobs.id'], ),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.PrimaryKeyConstraint('job_id', 'depends_on_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job_dependencies')
    op.drop_index(op.f('ix_jobs_type'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_job_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    # ### end Alembic commands ###
