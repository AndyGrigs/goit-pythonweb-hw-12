"""Add user roles

Revision ID: add_user_roles
Revises: 76219b0c3d31
Create Date: 2025-09-12 12:32:12.9487528

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'add_user_roles'
down_revision: Union[str, None] = '76219b0c3d31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Створюємо enum для ролей
    op.execute("CREATE TYPE userrole AS ENUM ('user', 'admin')")
    
    # Додаємо колонку role з дефолтним значенням 'user'
    op.add_column('users', sa.Column('role', sa.Enum('user', 'admin', name='userrole'), 
                                   nullable=False, server_default='user'))
    
    # Оновлюємо існуючих користувачів - встановлюємо роль 'admin' для першого користувача
    op.execute(text("""
        UPDATE users 
        SET role = 'admin' 
        WHERE id = (SELECT MIN(id) FROM users)
    """))


def downgrade() -> None:
    # Видаляємо колонку role
    op.drop_column('users', 'role')
    
    # Видаляємо enum тип
    op.execute("DROP TYPE userrole")