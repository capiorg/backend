from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import subqueryload

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import SessionDevice
from app.db.models import SessionTypeEnum
from app.db.models import UserSession


class UserSessionRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = UserSession

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    async def create_device(
        self,
        device_type: str,
        device_brand: str,
        device_family: str,
        os_family: str,
        os_version: str,
        browser_family: str,
        browser_version: str,
        ip: str,
        country: str,
        city: str,
    ) -> SessionDevice:
        model = SessionDevice(
            device_type=device_type,
            device_brand=device_brand,
            device_family=device_family,
            os_family=os_family,
            os_version=os_version,
            browser_family=browser_family,
            browser_version=browser_version,
            ip=ip,
            country=country,
            city=city,
        )
        self.base.session.add(model)
        await self.base.session.flush()
        return model

    @orm_error_handler
    async def create(
        self,
        user_uuid: UUID,
        code: str,
        device_type: str,
        device_brand: str,
        device_family: str,
        os_family: str,
        os_version: str,
        browser_family: str,
        browser_version: str,
        ip: str,
        country: str,
        city: str,
        session_type: SessionTypeEnum,
    ) -> UserSession:
        async with self.base.transaction_v2() as transaction:
            device = await self.create_device(
                device_type=device_type,
                device_brand=device_brand,
                device_family=device_family,
                os_family=os_family,
                os_version=os_version,
                browser_family=browser_family,
                browser_version=browser_version,
                ip=ip,
                country=country,
                city=city,
            )
            session = await self.base.insert(
                user_id=user_uuid,
                code=code,
                device_id=device.uuid,
                session_type=session_type,
            )
            await transaction.commit()
            return session

    @orm_error_handler
    async def get(self, uuid: UUID) -> UserSession:
        async with self.base.transaction_v2():
            return await self.base.get_one(self.model.uuid == uuid)

    @orm_error_handler
    async def get_all(self, uuid: UUID) -> list[UserSession]:
        async with self.base.transaction_v2() as transaction:
            stmt = (
                select(self.model)
                .options(subqueryload(self.model.device))
                .filter(self.model.user_id == uuid)
            )
            cur = await transaction.execute(stmt)
            return cur.scalars().all()

    @orm_error_handler
    async def activate(self, uuid: UUID):
        async with self.base.transaction_v2():
            return await self.base.update(
                self.model.uuid == uuid,
                status_id=1,
            )
