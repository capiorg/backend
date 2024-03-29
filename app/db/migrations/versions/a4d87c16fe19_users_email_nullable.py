"""users email nullable

Revision ID: a4d87c16fe19
Revises: 7cc19912eac3
Create Date: 2023-03-18 18:11:25.396531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4d87c16fe19"
down_revision = "7cc19912eac3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users", "phone", existing_type=sa.VARCHAR(length=20), nullable=False
    )
    op.drop_index("ix_users_email", table_name="users")
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=False)
    op.create_unique_constraint(None, "users", ["email"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.alter_column(
        "users", "phone", existing_type=sa.VARCHAR(length=20), nullable=True
    )
    # ### end Alembic commands ###
