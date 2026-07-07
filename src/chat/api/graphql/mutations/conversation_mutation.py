import strawberry
from strawberry.types import Info

from chat.api.graphql.context import get_conversation_service, get_read_state_service
from chat.api.graphql.types.conversation import Conversation, Participant


def _participants_from_ids(ids: list[str]) -> list[Participant]:
    return [Participant(user_id=strawberry.ID(uid)) for uid in ids]


@strawberry.type
class ConversationMutation:

    @strawberry.mutation
    async def create_direct_conversation(
        self,
        info: Info,
        user_a_id: str,
        user_b_id: str,
    ) -> Conversation:
        service = get_conversation_service(info)
        c = await service.create_direct_conversation(user_a_id, user_b_id)
        return Conversation(
            id=strawberry.ID(c.id),
            participants=_participants_from_ids(c.participant_ids),
            last_message=c.last_message,
            last_message_at=c.last_message_at,
            unread_count=c.unread_count,
        )

    @strawberry.mutation
    async def mark_read(
        self,
        info: Info,
        conversation_id: strawberry.ID,
        user_id: str,
    ) -> bool:
        service = get_read_state_service(info)
        return await service.mark_read(str(conversation_id), user_id)
