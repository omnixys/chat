from datetime import datetime

import strawberry

from chat.domain.enums import ChannelType
from chat.domain.enums import ConversationType as DomainConversationType

ConversationType = strawberry.enum(DomainConversationType)


@strawberry.type
class Participant:
    user_id: strawberry.ID


@strawberry.type
class Conversation:
    id: strawberry.ID
    type: ConversationType  # type: ignore[valid-type]
    participants: list[Participant]
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int
    channel: ChannelType
    external_address: str | None = None
    external_display_name: str | None = None
