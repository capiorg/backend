"""added session type nullable false

Revision ID: fef668643aba
Revises: d4cc52808a5d
Create Date: 2023-03-19 00:05:11.396531

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fef668643aba"
down_revision = "d4cc52808a5d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users_sessions",
        "session_type",
        existing_type=postgresql.ENUM(
            "REGISTER", "AUTH", name="sessiontypeenum"
        ),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users_sessions",
        "session_type",
        existing_type=postgresql.ENUM(
            "REGISTER", "AUTH", name="sessiontypeenum"
        ),
        nullable=True,
    )
    # ### end Alembic commands ###
