from chat.application.ports.delivery_policy import DeliveryPolicy
from chat.application.services.message_router import MessageRouter
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class MessageDispatcher:
    def __init__(self, policy: DeliveryPolicy, router: MessageRouter) -> None:
        self._policy = policy
        self._router = router

    async def dispatch(self, message: Message, conversation: Conversation) -> None:
        channels = await self._policy.determine_channels(message, conversation)
        for channel in channels:
            adapter = self._router.get_adapter(channel)
            await adapter.send(message, conversation)
