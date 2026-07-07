from datetime import datetime

import strawberry


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
