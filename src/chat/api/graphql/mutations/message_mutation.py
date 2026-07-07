import strawberry
from strawberry.types import Info

from chat.api.graphql.context import get_message_service
from chat.api.graphql.types.message import Message
from chat.domain.enums import ChannelType


@strawberry.type
class MessageMutation:

    @strawberry.mutation
    async def send_message(
        self,
        info: Info,
        conversation_id: strawberry.ID,
        sender_id: str,
        body: str,
        channel: ChannelType = ChannelType.IN_APP,
    ) -> Message:
        service = get_message_service(info)
        m = await service.send_message(
            str(conversation_id), sender_id, body, channel=channel,
        )
        return Message(
            id=strawberry.ID(m.id),
            conversation_id=strawberry.ID(m.conversation_id),
            sender_id=m.sender_id,
            body=m.body,
            content_type=m.content_type,
            channel=m.channel.type,
            delivery_status=m.delivery_status,
            created_at=m.created_at,
            edited_at=m.edited_at,
            deleted_at=m.deleted_at,
        )
