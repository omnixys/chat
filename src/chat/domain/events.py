from dataclasses import dataclass
from datetime import datetime

from chat.domain.enums import DeliveryStatus, MessageContentType
from chat.domain.models.communication_channel import CommunicationChannel


@dataclass
class MessageCreatedEvent:
    message_id: str
    conversation_id: str
    sender_id: str
    body: str
    content_type: MessageContentType
    channel: CommunicationChannel
    delivery_status: DeliveryStatus
    created_at: datetime
