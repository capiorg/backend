from sqlalchemy.orm import sessionmaker

from app.db.models import User
from app.v1.security.context import get_password_hash
from app.v1.users.repo import UserRepository


class UserService(UserRepository):
    def __init__(self, db_session: sessionmaker):
        super().__init__(db_session=db_session)

    async def create(
        self,
        login: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
        status_id: int,
    ) -> User:
        hashed_password = get_password_hash(password)
        return await super().create(
            login=login,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            status_id=status_id,
        )
