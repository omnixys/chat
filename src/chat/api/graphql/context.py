from dataclasses import dataclass, field

from strawberry.fastapi import BaseContext

from chat.application.ports.realtime_publisher import RealtimePublisher
from chat.application.services.conversation_service import ConversationService
from chat.application.services.message_service import MessageService
from chat.application.services.read_state_service import ReadStateService


@dataclass
class GraphQLContext(BaseContext):
    conversation_service: ConversationService = field(default=None)  # type: ignore[assignment]
    message_service: MessageService = field(default=None)  # type: ignore[assignment]
    read_state_service: ReadStateService = field(default=None)  # type: ignore[assignment]
    realtime: RealtimePublisher = field(default=None)  # type: ignore[assignment]


def get_conversation_service(info) -> ConversationService:
    ctx: GraphQLContext = info.context
    return ctx.conversation_service


def get_message_service(info) -> MessageService:
    ctx: GraphQLContext = info.context
    return ctx.message_service


def get_read_state_service(info) -> ReadStateService:
    ctx: GraphQLContext = info.context
    return ctx.read_state_service


def get_realtime_service(info) -> RealtimePublisher:
    ctx: GraphQLContext = info.context
    return ctx.realtime
