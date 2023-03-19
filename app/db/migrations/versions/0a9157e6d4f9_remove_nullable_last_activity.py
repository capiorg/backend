"""remove nullable last_activity

Revision ID: 0a9157e6d4f9
Revises: f9d09737883a
Create Date: 2023-03-15 03:00:26.508896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a9157e6d4f9'
down_revision = 'f9d09737883a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("alter table users alter column last_activity set not null;")
    op.execute("alter table users alter column is_online set not null;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
