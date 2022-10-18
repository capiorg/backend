from typing import List
from uuid import UUID

from sqlalchemy.orm import sessionmaker

from app.db.crud.base import BaseCRUD
from app.db.models import User


class UserRepository:
    def __init__(self, db_session: sessionmaker):
        super().__init__(db_session)

        self.db_session = db_session
        self.model = User

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    async def create(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> User:
        async with self.base.transaction_v2() as transaction:
            created_user = await self.base.insert(
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            await transaction.commit()
            return created_user
    
    async def get_one_from_uuid(self, uuid: UUID) -> User:
        async with self.base.transaction_v2():
            return await self.base.get_one(self.model.uuid == uuid)

    async def get_one_from_phone(self, phone: str) -> User:
        async with self.base.transaction_v2():
            return await self.base.get_one(self.model.phone == phone)

    async def get_all(self) -> List[User]:
        async with self.base.transaction_v2():
            return await self.base.get_many()
