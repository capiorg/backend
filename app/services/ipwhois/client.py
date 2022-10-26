from smsaero.rest.http import HTTPClient

from app.services.ipwhois.models import IPWhoisResponseModel


class IPWhoisSettings:
    URL = "https://ipwhois.pro/{ip}?key={api_key}&security=1&lang=en"
    HEADERS = {
        "accept": "*/*",
        "Referer": "https://ipwhois.io/",
    }


class IPWhoisClient(IPWhoisSettings, HTTPClient):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get(self, ip: str) -> IPWhoisResponseModel:
        response, code = await self._request(
            url=self.URL.format(ip=ip, api_key=self.api_key),
            method="GET",
            headers=self.HEADERS,
        )
        return IPWhoisResponseModel.parse_obj(response)
