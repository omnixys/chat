import strawberry
from strawberry.types import Info

from chat.api.graphql.context import get_conversation_service
from chat.api.graphql.types.conversation import Conversation, Participant


def _participants_from_ids(ids: list[str]) -> list[Participant]:
    return [Participant(user_id=strawberry.ID(uid)) for uid in ids]


@strawberry.type
class ConversationQuery:

    @strawberry.field
    async def conversations(self, info: Info, user_id: str) -> list[Conversation]:
        service = get_conversation_service(info)
        convos = await service.list_conversations(user_id)
        return [
            Conversation(
                id=strawberry.ID(c.id),
                participants=_participants_from_ids(c.participant_ids),
                last_message=c.last_message,
                last_message_at=c.last_message_at,
                unread_count=c.unread_count,
            )
            for c in convos
        ]

    @strawberry.field
    async def conversation(
        self, info: Info, id: strawberry.ID, user_id: str
    ) -> Conversation | None:
        service = get_conversation_service(info)
        c = await service.get_conversation(str(id), user_id)
        return Conversation(
            id=strawberry.ID(c.id),
            participants=_participants_from_ids(c.participant_ids),
            last_message=c.last_message,
            last_message_at=c.last_message_at,
            unread_count=c.unread_count,
        )
