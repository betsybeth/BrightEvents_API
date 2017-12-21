"""empty message

Revision ID: 148045bdbbb0
Revises: 
Create Date: 2017-12-20 22:01:28.432641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '148045bdbbb0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rsvps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone_no', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('category', sa.String(length=255), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    op.drop_table('rsvps')
    # ### end Alembic commands ###
