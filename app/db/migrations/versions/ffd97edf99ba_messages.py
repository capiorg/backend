"""messages

Revision ID: ffd97edf99ba
Revises: fef668643aba
Create Date: 2022-10-20 11:02:43.357752

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ffd97edf99ba"
down_revision = "fef668643aba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "messages",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "conversation_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("author", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.String(length=2048), nullable=True),
        sa.ForeignKeyConstraint(
            ["author"],
            ["users.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid", "conversation_id", "author"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    # ### end Alembic commands ###
