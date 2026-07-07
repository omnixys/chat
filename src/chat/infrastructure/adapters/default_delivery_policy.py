from chat.application.ports.delivery_policy import DeliveryPolicy
from chat.domain.models.communication_channel import CommunicationChannel
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class DefaultDeliveryPolicy(DeliveryPolicy):

    async def determine_channels(
        self,
        message: Message,
        conversation: Conversation,
    ) -> list[CommunicationChannel]:
        return [message.channel]
