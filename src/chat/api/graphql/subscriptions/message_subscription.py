from collections.abc import AsyncGenerator

import strawberry
from strawberry.types import Info

from chat.api.graphql.context import get_realtime_service
from chat.api.graphql.types.conversation import Conversation
from chat.api.graphql.types.message import Message
from chat.domain.events import MessageCreatedEvent


def _to_message_graphql(event: MessageCreatedEvent) -> Message:
    return Message(
        id=strawberry.ID(event.message_id),
        conversation_id=strawberry.ID(event.conversation_id),
        sender_id=event.sender_id,
        body=event.body,
        content_type=event.content_type,
        channel=event.channel.type,
        delivery_status=event.delivery_status,
        created_at=event.created_at,
    )


def _to_conversation_graphql(event: MessageCreatedEvent) -> Conversation:
    return Conversation(
        id=strawberry.ID(event.conversation_id),
        participants=[],
        last_message=event.body,
        last_message_at=event.created_at,
        unread_count=0,
    )


@strawberry.type
class MessageSubscription:

    @strawberry.subscription
    async def message_received(
        self, info: Info, conversation_id: strawberry.ID
    ) -> AsyncGenerator[Message]:
        realtime = get_realtime_service(info)
        channel = f"conversation:{conversation_id}"
        async for event in realtime.subscribe(channel):
            yield _to_message_graphql(event)

    @strawberry.subscription
    async def conversation_updated(
        self, info: Info, user_id: strawberry.ID
    ) -> AsyncGenerator[Conversation]:
        realtime = get_realtime_service(info)
        channel = f"user:{user_id}"
        async for event in realtime.subscribe(channel):
            yield _to_conversation_graphql(event)
