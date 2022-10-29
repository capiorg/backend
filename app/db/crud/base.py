import logging
from abc import ABC
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncContextManager
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import lambda_stmt
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSessionTransaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Executable

Model = TypeVar("Model")
TransactionContext = AsyncContextManager[AsyncSessionTransaction]

logger = logging.getLogger(__name__)


class BaseCRUD(ABC):
    def __init__(
        self,
        db_session: Union[sessionmaker, AsyncSession],
        model: Type[Model],
    ):
        self.model = model

        if isinstance(db_session, sessionmaker):
            self.session: AsyncSession = cast(AsyncSession, db_session())
        else:
            self.session = db_session

    def transaction_v2(self) -> AsyncContextManager[AsyncSession]:
        @asynccontextmanager
        async def transaction() -> AsyncContextManager[AsyncSession]:
            async with self.session as session:  # type: AsyncSession
                try:
                    yield session
                except Exception as exc:  # noqa
                    logger.error(f"Произошла ошибка в транзакции: {exc}")
                    await session.rollback()
                    raise exc
                finally:
                    await session.commit()

        return transaction()

    async def insert(self, **kwargs: Any) -> Model:
        add_model = self._convert_to_model(**kwargs)
        self.session.add(add_model)
        return add_model

    async def get_one(
        self, *args, transaction: Optional[AsyncSession] = None
    ) -> Model:
        stmt = select(self.model).where(*args)
        cursor = await self.execute(stmt=stmt, transaction=transaction)
        return cursor.scalar_one()

    async def get_many(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> Model:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*args)
        query_stmt = cast(Executable, stmt)

        cursor = await self.execute(stmt=query_stmt, transaction=transaction)
        return cursor.scalars().all()

    async def _update(
        self,
        *args: Any,
        transaction: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Result:
        stmt = (
            update(self.model)
            .where(*args)
            .values(**kwargs)
            .returning(self.model)
        )

        stmt = (
            select(self.model)
            .from_statement(stmt)
            .execution_options(synchronize_session="fetch")
        )

        cursor = await self.execute(stmt=stmt, transaction=transaction)
        return cursor

    async def update(
        self,
        *args: Any,
        transaction: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Model:
        res = await self._update(*args, transaction=transaction, **kwargs)
        return res.scalar_one()

    async def update_many(
        self,
        *args: Any,
        transaction: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Model:
        res = await self._update(*args, transaction=transaction, **kwargs)
        return res.scalars().all()

    async def exists(
        self,
        *args: Any,
        transaction: Optional[AsyncSession] = None,
    ) -> Optional[bool]:
        stmt = self.exists_stmt(*args)
        curr = await self.execute(stmt=stmt, transaction=transaction)
        result = curr.scalar_one()
        return cast(Optional[bool], result)

    def exists_stmt(self, *args):
        return exists(1).select_from(self.model).where(*args).select()

    async def exists_get(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> List[Model]:
        """Check is row exists in database. If it does, returns the row"""
        stmt = select(self.model).where(*args)
        curr = await self.execute(stmt=stmt, transaction=transaction)
        result = curr.scalars().all()
        return result

    async def base_delete(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> Result:
        stmt = delete(self.model).where(*args).returning("*")
        curr = await self.execute(stmt=stmt, transaction=transaction)

        return curr

    async def delete_many(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> List[Union[UUID, int, str]]:
        result = await self.base_delete(*args, transaction=transaction)
        result = result.scalars().all()
        return result

    async def delete_one(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> Union[UUID, int, str]:
        result = await self.base_delete(*args, transaction=transaction)
        result = result.scalar_one()
        return result

    async def soft_cascade_delete(
        self,
        *args: Any,
        status: int = 0,
        transaction: Optional[AsyncSession] = None,
    ) -> Model:
        return await self.update(
            *args, transaction=transaction, status_id=status
        )

    async def soft_cascade_delete_many(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> List[Model]:
        return await self.update_many(
            *args, transaction=transaction, status_id=0
        )

    async def count(
        self, *args: Any, transaction: Optional[AsyncSession] = None
    ) -> int:
        stmt = select(func.count()).select_from(
            select(self.model).where(*args).subquery()
        )
        cursor = await self.execute(stmt=stmt, transaction=transaction)
        count = cursor.scalar_one()
        return cast(int, count)

    def _convert_to_model(self, **kwargs) -> Model:
        return self.model(**kwargs)

    async def execute(
        self, stmt: Any, transaction: Optional[AsyncSession] = None
    ) -> Result:
        if transaction:
            curr = await transaction.execute(stmt)
        else:
            curr = await self.session.execute(stmt)
        return curr
