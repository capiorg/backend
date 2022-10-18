from app.db.models import User
from app.v1.security.context import get_password_hash
from app.v1.users.repo import UserRepository


class UserService(UserRepository):
    async def create(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> User:
        hashed_password = get_password_hash(password)
        return await super().create(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password
        )
