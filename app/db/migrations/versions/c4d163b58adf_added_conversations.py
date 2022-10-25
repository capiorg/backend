"""added conversations

Revision ID: c4d163b58adf
Revises: b914362163df
Create Date: 2022-10-18 09:57:42.281651

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4d163b58adf'
down_revision = 'b914362163df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversations',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('chat_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.uuid'], ),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.uuid'], ),
    sa.ForeignKeyConstraint(['type_id'], ['chats_types.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.drop_table('chats_users')
    op.drop_constraint('chats_type_id_fkey', 'chats', type_='foreignkey')
    op.drop_column('chats', 'type_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('type_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('chats_type_id_fkey', 'chats', 'chats_types', ['type_id'], ['id'])
    op.create_table('chats_users',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('chat_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('status_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.uuid'], name='chats_users_chat_id_fkey'),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], name='chats_users_status_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], name='chats_users_user_id_fkey')
    )
    op.drop_table('conversations')
    # ### end Alembic commands ###
