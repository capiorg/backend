from enum import Enum
from typing import Optional

from user_agents import parse
from user_agents.parsers import Browser
from user_agents.parsers import Device
from user_agents.parsers import OperatingSystem


class UserAgentTypes(str, Enum):
    PC = "PC"
    TABLET = "TABLET"
    BOT = "BOT"
    MOBILE = "MOBILE"
    EMAIL_CLIENT = "EMAIL_CLIENT"
    TOUCH_CAPABLE = "TOUCH_CAPABLE"


class UserAgentInformation:
    def __init__(self, v: str):
        self.v = parse(v)

    @property
    def type(self) -> Optional[UserAgentTypes]:
        if self.v.is_pc:
            return UserAgentTypes.PC
        if self.v.is_tablet:
            return UserAgentTypes.TABLET
        if self.v.is_bot:
            return UserAgentTypes.BOT
        if self.v.is_mobile:
            return UserAgentTypes.MOBILE
        if self.v.is_email_client:
            return UserAgentTypes.EMAIL_CLIENT
        if self.v.is_touch_capable:
            return UserAgentTypes.TOUCH_CAPABLE
        return None

    @property
    def device(self) -> Device:
        return self.v.device

    @property
    def os(self) -> OperatingSystem:
        return self.v.os

    @property
    def browser(self) -> Browser:
        return self.v.browser
