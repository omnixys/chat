from abc import ABC, abstractmethod

from chat.domain.enums import ChannelType
from chat.domain.models.channel_capabilities import ChannelCapabilities
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class ChannelAdapter(ABC):
    @property
    @abstractmethod
    def channel_type(self) -> ChannelType: ...

    @abstractmethod
    async def capabilities(self) -> ChannelCapabilities: ...

    @abstractmethod
    async def send(self, message: Message, conversation: Conversation) -> None: ...
