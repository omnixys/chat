from datetime import datetime

import strawberry
from strawberry.types import Info

from chat.api.graphql.context import get_message_service
from chat.api.graphql.types.message import Message


@strawberry.type
class MessageQuery:

    @strawberry.field
    async def messages(
        self,
        info: Info,
        conversation_id: strawberry.ID,
        user_id: str,
        limit: int = 50,
        before: datetime | None = None,
    ) -> list[Message]:
        service = get_message_service(info)
        msgs = await service.get_messages(str(conversation_id), user_id, limit=limit, before=before)
        return [
            Message(
                id=strawberry.ID(m.id),
                conversation_id=strawberry.ID(m.conversation_id),
                sender_id=m.sender_id,
                body=m.body,
                content_type=m.content_type,
                created_at=m.created_at,
                edited_at=m.edited_at,
                deleted_at=m.deleted_at,
            )
            for m in msgs
        ]
