from datetime import datetime

import strawberry

from chat.domain.enums import ChannelType


@strawberry.type
class Participant:
    user_id: strawberry.ID


@strawberry.type
class Conversation:
    id: strawberry.ID
    participants: list[Participant]
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int
    channel: ChannelType
    external_address: str | None = None
    external_display_name: str | None = None
