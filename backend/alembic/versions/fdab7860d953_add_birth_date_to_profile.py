"""add birth_date to profile

Revision ID: fdab7860d953
Revises: 8567a89d30e5
Create Date: 2025-03-10 23:47:08.552587

"""
from alembic import op
import sqlalchemy as sa
from app.core.config import settings


# revision identifiers, used by Alembic.
revision = 'fdab7860d953'
down_revision = '8567a89d30e5'
branch_labels = None
depends_on = None


def upgrade():
    # Add column as nullable first
    op.add_column('profile_pictures', sa.Column('backend_url', sa.String(), nullable=True))
    
    # Update existing records with backend_url
    op.execute("""
        UPDATE profile_pictures 
        SET backend_url = CONCAT(
            '{backend_url}/media/', 
            file_path
        )
    """.format(backend_url=settings.BACKEND_URL))
    
    # Make column non-nullable
    op.alter_column('profile_pictures', 'backend_url',
                    existing_type=sa.String(),
                    nullable=False)

def downgrade():
    op.drop_column('profile_pictures', 'backend_url')