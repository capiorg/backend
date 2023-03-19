from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import User


class UserRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = User

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    @orm_error_handler
    async def create(
        self,
        login: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
        status_id: int,
    ) -> User:
        async with self.base.transaction_v2() as transaction:
            created_user = await self.base.insert(
                login=login,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                password=password,
                status_id=status_id,
            )
            await transaction.commit()
            return created_user

    @orm_error_handler
    async def get_one_from_uuid(self, uuid: UUID) -> User:
        async with self.base.transaction_v2() as transaction:
            stmt = (
                select(User)
                .options(joinedload(User.avatar), joinedload(User.role))
                .filter(User.uuid == uuid)
            )
            curr = await transaction.execute(stmt)
            return curr.scalar_one()

    @orm_error_handler
    async def get_one_from_phone(self, phone: str) -> User:
        async with self.base.transaction_v2():
            return await self.base.get_one(self.model.phone == phone)

    @orm_error_handler
    async def get_all(self) -> List[User]:
        async with self.base.transaction_v2():
            return await self.base.get_many()

    @orm_error_handler
    async def activate(self, uuid: UUID) -> User:
        async with self.base.transaction_v2() as transaction:
            result = await self.base.update(
                self.model.uuid == uuid, status_id=1
            )
            await transaction.commit()
            return result
