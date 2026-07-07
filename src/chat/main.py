from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from chat.api.graphql.context import GraphQLContext
from chat.api.graphql.schema import schema
from chat.api.health import router as health_router
from chat.application.services.conversation_service import ConversationService
from chat.application.services.message_dispatcher import MessageDispatcher
from chat.application.services.message_router import MessageRouter
from chat.application.services.message_service import MessageService
from chat.application.services.read_state_service import ReadStateService
from chat.database import async_session_factory, engine
from chat.domain.enums import ChannelType
from chat.infrastructure.adapters.default_delivery_policy import DefaultDeliveryPolicy
from chat.infrastructure.adapters.email_channel_adapter import EmailChannelAdapter
from chat.infrastructure.adapters.in_app_channel_adapter import InAppChannelAdapter
from chat.infrastructure.adapters.sms_channel_adapter import SmsChannelAdapter
from chat.infrastructure.adapters.whatsapp_channel_adapter import WhatsAppChannelAdapter
from chat.infrastructure.db.repositories.conversation_repository import (
    SqlAlchemyConversationRepository,
)
from chat.infrastructure.db.repositories.message_repository import (
    SqlAlchemyMessageRepository,
)
from chat.infrastructure.db.repositories.read_state_repository import (
    SqlAlchemyReadStateRepository,
)
from chat.infrastructure.realtime.in_memory_event_bus import InMemoryEventBus

realtime = InMemoryEventBus()

in_app_adapter = InAppChannelAdapter(realtime)
whatsapp_adapter = WhatsAppChannelAdapter()
email_adapter = EmailChannelAdapter()
sms_adapter = SmsChannelAdapter()

router = MessageRouter({
    ChannelType.IN_APP: in_app_adapter,
    ChannelType.WHATSAPP: whatsapp_adapter,
    ChannelType.EMAIL: email_adapter,
    ChannelType.SMS: sms_adapter,
})

policy = DefaultDeliveryPolicy()
dispatcher = MessageDispatcher(policy, router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(title="Omnixys Chat", version="0.1.0", lifespan=lifespan)

    app.include_router(health_router)

    async def get_context() -> AsyncGenerator[GraphQLContext]:
        async with async_session_factory() as session:
            conversation_repo = SqlAlchemyConversationRepository(session)
            message_repo = SqlAlchemyMessageRepository(session)
            read_state_repo = SqlAlchemyReadStateRepository(session)

            yield GraphQLContext(
                conversation_service=ConversationService(
                    session=session,
                    conversation_repo=conversation_repo,
                    message_repo=message_repo,
                    read_state_repo=read_state_repo,
                ),
                message_service=MessageService(
                    session=session,
                    conversation_repo=conversation_repo,
                    message_repo=message_repo,
                    read_state_repo=read_state_repo,
                    dispatcher=dispatcher,
                ),
                read_state_service=ReadStateService(
                    session=session,
                    conversation_repo=conversation_repo,
                    message_repo=message_repo,
                    read_state_repo=read_state_repo,
                ),
                realtime=realtime,
            )

    graphql_router = GraphQLRouter(
        schema,
        context_getter=get_context,
        subscription_protocols=["graphql-transport-ws"],
    )
    app.include_router(graphql_router, prefix="/graphql")

    return app


app = create_application()


def run() -> None:
    import asyncio

    import hypercorn.asyncio
    import hypercorn.config

    from chat.config import settings

    config = hypercorn.config.Config()
    config.bind = [f"{settings.host}:{settings.port}"]
    config.loglevel = settings.log_level.lower()

    asyncio.run(hypercorn.asyncio.serve(app, config))
