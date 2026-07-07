from enum import StrEnum


class ConversationType(StrEnum):
    DIRECT = "DIRECT"
    GROUP = "GROUP"
    CHANNEL = "CHANNEL"
    SUPPORT = "SUPPORT"


class MessageContentType(StrEnum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    FILE = "FILE"
    SYSTEM = "SYSTEM"


class ChannelType(StrEnum):
    IN_APP = "IN_APP"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    SMS = "SMS"


class DeliveryStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
