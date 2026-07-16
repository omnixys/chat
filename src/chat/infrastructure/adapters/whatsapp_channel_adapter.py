from __future__ import annotations

import logging

from chat.application.ports.channel_adapter import ChannelAdapter
from chat.domain.enums import ChannelType, DeliveryStatus
from chat.domain.models.channel_capabilities import ChannelCapabilities
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message
from chat.infrastructure.gateway.gateway_client import GatewayClient

logger = logging.getLogger(__name__)


class WhatsAppChannelAdapter(ChannelAdapter):
    def __init__(self, gateway_client: GatewayClient) -> None:
        self._gateway = gateway_client

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
        extra = dict(
            message_id=message.id,
            conversation_id=message.conversation_id,
            channel="WHATSAPP",
        )
        logger.info("adapter_whatsapp_send_start %s", extra)
        result = await self._gateway.send(message, conversation)
        if result.success:
            message.delivery_status = result.status
            message.provider_message_id = result.provider_message_id
            logger.info("adapter_whatsapp_send_sent status=%s %s", result.status.value, extra)
        else:
            message.delivery_status = DeliveryStatus.FAILED
            logger.warning("adapter_whatsapp_send_failed error=%s %s", result.error, extra)
