from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from chat.config import settings
from chat.domain.enums import DeliveryStatus
from chat.domain.models.conversation import Conversation
from chat.domain.models.message import Message

logger = logging.getLogger(__name__)


@dataclass
class GatewayResult:
    success: bool
    status: DeliveryStatus
    error: str | None = None
    raw: dict[str, Any] | None = field(default_factory=dict)
    provider_message_id: str | None = None


class GatewayError(Exception):
    pass


class GatewayClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.communication_gateway_url.rstrip("/"),
            headers={
                "x-internal-api-key": settings.communication_gateway_api_key,
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(settings.communication_gateway_timeout),
        )

    async def send(self, message: Message, conversation: Conversation) -> GatewayResult:
        payload = {
            "id": message.id,
            "channel": message.channel.type.value,
            "recipientAddress": conversation.external_address,
            "senderId": message.sender_id,
            "body": message.body,
            "contentType": message.content_type.value,
            "metadata": {"conversationId": conversation.id},
        }

        extra = {
            "message_id": message.id,
            "conversation_id": message.conversation_id,
            "channel": message.channel.type.value,
        }
        logger.info("gateway_outbound_start %s", extra)

        try:
            response = await self._client.post(
                "/api/v1/messages/send",
                json=payload,
            )
            data = response.json()
            logger.info(
                "gateway_outbound_response status=%s %s",
                response.status_code,
                extra,
            )

            if response.is_success and data.get("success"):
                delivery = DeliveryStatus(data.get("status", "SENT"))
                return GatewayResult(
                    success=True,
                    status=delivery,
                    raw=data,
                    provider_message_id=data.get("providerMessageId"),
                )

            error_msg = data.get("error") or f"HTTP {response.status_code}"
            return GatewayResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error=error_msg,
                raw=data,
            )

        except httpx.TimeoutException:
            logger.warning("gateway_outbound_timeout %s", extra)
            return GatewayResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error="gateway_timeout",
            )

        except httpx.ConnectError:
            logger.warning("gateway_outbound_unreachable %s", extra)
            return GatewayResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error="gateway_unreachable",
            )

        except Exception as exc:
            logger.error("gateway_outbound_error exc=%s %s", exc, extra)
            return GatewayResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error=f"gateway_error: {exc}",
            )

    async def close(self) -> None:
        await self._client.aclose()
