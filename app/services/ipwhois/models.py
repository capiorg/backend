from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Flag(BaseModel):
    img: str
    emoji: str
    emoji_unicode: str


class Connection(BaseModel):
    asn: int
    org: str
    isp: str
    domain: str


class Timezone(BaseModel):
    id: str
    abbr: str
    is_dst: bool
    offset: int
    utc: str
    current_time: str


class Currency(BaseModel):
    name: str
    code: str
    symbol: str
    plural: str
    exchange_rate: float


class Security(BaseModel):
    anonymous: bool
    proxy: bool
    vpn: bool
    tor: bool
    hosting: bool


class IPWhoisResponseModel(BaseModel):
    ip: Optional[str] = None
    success: Optional[bool] = None
    type: Optional[str] = None
    continent: Optional[str] = None
    continent_code: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    region_code: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_eu: Optional[bool] = None
    postal: Optional[str] = None
    calling_code: Optional[str] = None
    capital: Optional[str] = None
    borders: Optional[str] = None
    flag: Optional[Flag] = None
    connection: Optional[Connection] = None
    timezone: Optional[Timezone] = None
    currency: Optional[Currency] = None
    security: Optional[Security] = None
