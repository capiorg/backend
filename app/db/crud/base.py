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

    async def get_one(self, *args) -> Model:
        stmt = select(self.model).where(*args)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_many(self, *args: Any) -> Model:
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*args)
        query_stmt = cast(Executable, stmt)

        result = await self.session.execute(query_stmt)
        return result.scalars().all()

    async def _update(self, *args: Any, **kwargs: Any) -> Model:
        stmt = update(self.model).where(*args).values(**kwargs).returning(self.model)

        stmt = (
            select(self.model)
            .from_statement(stmt)
            .execution_options(synchronize_session="fetch")
        )

        result = await self.session.execute(stmt)
        return result

    async def update(self, *args: Any, **kwargs: Any) -> Model:
        res = await self._update(*args, **kwargs)
        return res.scalar_one()

    async def update_many(self, *args: Any, **kwargs: Any) -> Model:
        res = await self._update(*args, **kwargs)
        return res.scalars().all()

    async def exists(self, *args: Any) -> Optional[bool]:
        """Check is row exists in database"""
        stmt = exists(select(self.model).where(*args)).select()
        result_stmt = await self.session.execute(stmt)
        result = result_stmt.scalar()
        return cast(Optional[bool], result)

    async def exists_get(self, *args: Any) -> List[Model]:
        """Check is row exists in database. If it does, returns the row"""
        stmt = select(self.model).where(*args)
        result_stmt = await self.session.execute(stmt)
        result = result_stmt.scalars().all()
        return result

    async def base_delete(self, *args: Any) -> Result:
        stmt = delete(self.model).where(*args).returning("*")
        result = await self.session.execute(stmt)

        return result

    async def delete_many(self, *args: Any) -> List[Union[UUID, int, str]]:
        result = await self.base_delete(*args)
        result = result.scalars().all()
        return result

    async def delete_one(self, *args: Any) -> Union[UUID, int, str]:
        result = await self.base_delete(*args)
        result = result.scalar_one()
        return result

    async def soft_cascade_delete(self, *args: Any, status: int = 0) -> Model:
        return await self.update(*args, status_id=status)

    async def soft_cascade_delete_many(self, *args: Any) -> List[Model]:
        return await self.update_many(*args, status_id=0)

    async def count(self, *args: Any) -> int:
        stmt = select(func.count()).select_from(
            select(self.model).where(*args).subquery()
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return cast(int, count)

    def _convert_to_model(self, **kwargs) -> Model:
        return self.model(**kwargs)
