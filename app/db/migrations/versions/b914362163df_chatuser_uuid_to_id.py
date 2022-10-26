"""chatuser uuid to id

Revision ID: b914362163df
Revises: c4c1e9c0a2d9
Create Date: 2022-10-18 07:57:47.818338

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b914362163df"
down_revision = "c4c1e9c0a2d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("chats_users", sa.Column("id", sa.Integer(), nullable=False))
    op.drop_column("chats_users", "uuid")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "chats_users",
        sa.Column(
            "uuid", postgresql.UUID(), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("chats_users", "id")
    # ### end Alembic commands ###
