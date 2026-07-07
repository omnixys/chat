from dataclasses import dataclass

from chat.domain.enums import ChannelType


@dataclass(frozen=True)
class CommunicationChannel:
    type: ChannelType
