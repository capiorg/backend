import random
from uuid import UUID

from smsaero.client import SMSAero

from app.db.models import SessionTypeEnum
from app.db.models import User
from app.db.models import UserSession
from app.services.ipwhois.client import IPWhoisClient
from app.utils.u_agents import UserAgentInformation
from app.v1.security.repo import UserSessionRepository


def generate_code():
    return str(random.randint(1000, 9999))


class UserSessionService:
    def __init__(
        self,
        repo: UserSessionRepository,
        sms_aero: SMSAero,
        whois: IPWhoisClient,
    ):
        self.sms_aero = sms_aero
        self.repo = repo
        self.whois = whois

    async def authorize(
        self,
        user: User,
        user_agent: str,
        ip_address: str,
    ) -> UserSession:
        return await self.create(
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
            session_type=SessionTypeEnum.AUTH,
        )

    async def register(
        self,
        user: User,
        user_agent: str,
        ip_address: str,
    ) -> UserSession:
        return await self.create(
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
            session_type=SessionTypeEnum.REGISTER,
        )

    async def create(
        self,
        user: User,
        user_agent: str,
        ip_address: str,
        session_type: SessionTypeEnum,
    ) -> UserSession:
        fingerprint = UserAgentInformation(v=user_agent)
        ip_info = await self.whois.get(ip=ip_address)

        random_code = generate_code()

        await self.send_code(phone=user.phone, code=random_code)
        return await self.repo.create(
            user_uuid=user.uuid,
            code=random_code,
            device_type=fingerprint.type,
            device_brand=fingerprint.device.brand,
            device_family=fingerprint.device.family,
            os_family=fingerprint.os.family,
            os_version=fingerprint.os.version_string,
            browser_family=fingerprint.browser.family,
            browser_version=fingerprint.browser.version_string,
            ip=ip_info.ip,
            country=ip_info.country,
            city=ip_info.city,
            session_type=session_type,
        )

    async def send_code(self, phone: str, code: str) -> None:
        await self.sms_aero.flash_call.send(phone=phone, code=code)

    async def get(self, uuid: UUID) -> UserSession:
        return await self.repo.get(uuid=uuid)

    async def activate_code(self, uuid: UUID):
        return await self.repo.activate(uuid=uuid)
