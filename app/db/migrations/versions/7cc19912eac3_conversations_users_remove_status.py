"""conversations_users remove status

Revision ID: 7cc19912eac3
Revises: ac7751f784a3
Create Date: 2023-03-18 18:45:12.396531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7cc19912eac3"
down_revision = "ac7751f784a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "users_conversations_status_id_fkey",
        "users_conversations",
        type_="foreignkey",
    )
    op.drop_column("users_conversations", "status_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users_conversations",
        sa.Column(
            "status_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "users_conversations_status_id_fkey",
        "users_conversations",
        "statuses",
        ["status_id"],
        ["id"],
    )
    # ### end Alembic commands ###
