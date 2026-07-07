from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.application.ports.read_state_repository import (
    ReadStateRepository as ReadStateRepositoryPort,
)
from chat.domain.models.read_state import ReadState
from chat.domain.utils import generate_uuid
from chat.infrastructure.db.models import ReadStateModel


class SqlAlchemyReadStateRepository(ReadStateRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find(self, conversation_id: str, user_id: str) -> ReadState | None:
        stmt = (
            select(ReadStateModel)
            .where(
                ReadStateModel.conversation_id == conversation_id,
                ReadStateModel.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ReadState(
            id=row.id,
            conversation_id=row.conversation_id,
            user_id=row.user_id,
            last_read_at=row.last_read_at,
            last_read_message_id=row.last_read_message_id,
        )

    async def upsert(self, read_state: ReadState) -> ReadState:
        existing = await self.find(read_state.conversation_id, read_state.user_id)
        if existing is not None:
            existing.last_read_at = read_state.last_read_at
            existing.last_read_message_id = read_state.last_read_message_id
            await self.session.flush()
            return existing
        model = ReadStateModel(
            id=generate_uuid(),
            conversation_id=read_state.conversation_id,
            user_id=read_state.user_id,
            last_read_at=read_state.last_read_at,
            last_read_message_id=read_state.last_read_message_id,
        )
        self.session.add(model)
        await self.session.flush()
        return read_state
