from chat.application.ports.channel_adapter import ChannelAdapter
from chat.domain.enums import ChannelType
from chat.domain.models.channel_capabilities import ChannelCapabilities
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message


class WhatsAppChannelAdapter(ChannelAdapter):

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.WHATSAPP

    async def capabilities(self) -> ChannelCapabilities:
        return ChannelCapabilities(
            supports_attachments=True,
            supports_rich_text=False,
            supports_formatting=False,
            supports_typing=True,
            supports_read_receipts=True,
            supports_reactions=False,
            supports_quoted_replies=True,
            supports_forwarding=False,
            supports_editing=False,
            supports_deletion=False,
            supports_delivery_status=True,
            supports_presence=True,
        )

    async def send(self, message: Message, conversation: Conversation) -> None:
        raise NotImplementedError("WhatsApp adapter — to be implemented in Communication Gateway")
