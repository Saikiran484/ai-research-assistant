"""add extracted_text to documents

Revision ID: 002_add_extracted_text
Revises: 001_create_documents
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_extracted_text"
down_revision: Union[str, None] = "001_create_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("parse_error", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "parse_error")
    op.drop_column("documents", "extracted_text")
