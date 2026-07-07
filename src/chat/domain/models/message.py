from dataclasses import dataclass, field
from datetime import datetime

from chat.domain.enums import ChannelType, DeliveryStatus, MessageContentType
from chat.domain.models.communication_channel import CommunicationChannel
from chat.domain.utils import generate_uuid, utcnow


@dataclass
class Message:
    id: str = field(default_factory=generate_uuid)
    conversation_id: str = ""
    sender_id: str = ""
    body: str = ""
    content_type: MessageContentType = MessageContentType.TEXT
    channel: CommunicationChannel = field(
        default_factory=lambda: CommunicationChannel(type=ChannelType.IN_APP)
    )
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    created_at: datetime = field(default_factory=utcnow)
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
