from typing import Any
from socketio import AsyncRedisManager


class RedisSocketQueue:
    def __init__(self, mgr: AsyncRedisManager):
        self.mgr = mgr

    async def emit(
        self,
        event: str,
        data: Any,
        namespace: str = None,
        room: str = None,
        skip_sid: str = None,
        callback=None,
        **kwargs
    ):
        return await self.mgr.emit(
            event=event,
            data=data,
            namespace=namespace,
            room=room,
            skip_sid=skip_sid,
            callback=callback,
            **kwargs
        )
