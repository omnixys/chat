from abc import ABC, abstractmethod


class PresenceService(ABC):

    @abstractmethod
    async def set_online(self, user_id: str) -> None: ...

    @abstractmethod
    async def set_offline(self, user_id: str) -> None: ...

    @abstractmethod
    async def heartbeat(self, user_id: str) -> None: ...


class NullPresenceService(PresenceService):

    async def set_online(self, user_id: str) -> None:
        pass

    async def set_offline(self, user_id: str) -> None:
        pass

    async def heartbeat(self, user_id: str) -> None:
        pass
