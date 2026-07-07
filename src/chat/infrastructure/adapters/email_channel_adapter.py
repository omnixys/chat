from chat.application.ports.channel_adapter import ChannelAdapter
from chat.domain.enums import ChannelType
from chat.domain.models.channel_capabilities import ChannelCapabilities
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class EmailChannelAdapter(ChannelAdapter):

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.EMAIL

    async def capabilities(self) -> ChannelCapabilities:
        return ChannelCapabilities(
            supports_attachments=True,
            supports_rich_text=True,
            supports_formatting=True,
            supports_typing=False,
            supports_read_receipts=False,
            supports_reactions=False,
            supports_quoted_replies=True,
            supports_forwarding=True,
            supports_editing=False,
            supports_deletion=False,
            supports_delivery_status=False,
            supports_presence=False,
        )

    async def send(self, message: Message, conversation: Conversation) -> None:
        raise NotImplementedError("Email adapter — to be implemented in Communication Gateway")
