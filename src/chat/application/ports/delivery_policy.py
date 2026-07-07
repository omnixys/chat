from abc import ABC, abstractmethod

from chat.domain.models.communication_channel import CommunicationChannel
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class DeliveryPolicy(ABC):

    @abstractmethod
    async def determine_channels(
        self,
        message: Message,
        conversation: Conversation,
    ) -> list[CommunicationChannel]: ...
