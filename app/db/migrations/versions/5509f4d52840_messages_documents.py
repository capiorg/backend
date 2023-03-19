"""messages_documents

Revision ID: 5509f4d52840
Revises: 0a9157e6d4f9
Create Date: 2023-03-18 22:11:25.396531

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5509f4d52840'
down_revision = '0a9157e6d4f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'messages_documents',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.uuid'], ),
        sa.ForeignKeyConstraint(['message_id'], ['messages.uuid'], ),
        sa.PrimaryKeyConstraint('uuid', 'message_id', 'document_id')
        )
    op.alter_column(
        'users', 'is_online',
        existing_type=sa.BOOLEAN(),
        nullable=True
        )
    op.alter_column(
        'users', 'last_activity',
        existing_type=postgresql.TIMESTAMP(),
        nullable=True
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'users', 'last_activity',
        existing_type=postgresql.TIMESTAMP(),
        nullable=False
        )
    op.alter_column(
        'users', 'is_online',
        existing_type=sa.BOOLEAN(),
        nullable=False
        )
    op.drop_table('messages_documents')
    # ### end Alembic commands ###