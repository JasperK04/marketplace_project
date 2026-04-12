"""add image data and filename, drop filepath

Revision ID: 20260412_add_image_data
Revises:
Create Date: 2026-04-12 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "20260412_add_image_data"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "image" not in inspector.get_table_names():
        # nothing to do if table doesn't exist
        return
    cols = [c["name"] for c in inspector.get_columns("image")]

    if "data" not in cols:
        op.add_column("image", sa.Column("data", sa.LargeBinary(), nullable=True))

    if "filename" not in cols:
        op.add_column("image", sa.Column("filename", sa.String(), nullable=True))

    # drop legacy filepath column if present (use batch for SQLite)
    if "filepath" in cols:
        with op.batch_alter_table("image") as batch_op:
            batch_op.drop_column("filepath")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "image" not in inspector.get_table_names():
        return
    cols = [c["name"] for c in inspector.get_columns("image")]

    # add back filepath if missing
    if "filepath" not in cols:
        with op.batch_alter_table("image") as batch_op:
            batch_op.add_column(sa.Column("filepath", sa.String(), nullable=True))

    if "data" in cols:
        with op.batch_alter_table("image") as batch_op:
            batch_op.drop_column("data")

    if "filename" in cols:
        with op.batch_alter_table("image") as batch_op:
            batch_op.drop_column("filename")
