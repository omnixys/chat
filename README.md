# Omnixys Chat Service

Isolierter Chat-Microservice (V1 Prototyp).

## Technologie

- **Python 3.14**
- **FastAPI** (HTTP + WebSocket Transport)
- **Strawberry GraphQL** (Schema, Resolver, Subscriptions)
- **PostgreSQL** (Datenhaltung)
- **SQLAlchemy 2.0 Async** (ORM)
- **Alembic** (Migrationen)
- **Hypercorn** (ASGI Server)
- **uv** (Package Manager)

## Architektur

```
src/chat/
├── main.py                         # FastAPI App + Application Container
├── config.py                       # Pydantic Settings
├── database.py                     # Async Engine + Session Factory
├── api/
│   ├── health.py                   # GET /health, /health/live, /health/ready
│   └── graphql/
│       ├── schema.py               # Strawberry Schema Assembly
│       ├── context.py              # GraphQL Context (Services)
│       ├── types/                  # GraphQL Type Definitions
│       ├── queries/                # Query Resolver
│       ├── mutations/              # Mutation Resolver
│       └── subscriptions/          # Subscription Resolver
├── domain/
│   ├── enums.py                    # ConversationType
│   ├── errors.py                   # Domain-Exceptions
│   └── models/                     # Domain-Dataclasses
├── application/
│   ├── ports/                      # Interfaces (Repository, Publisher)
│   └── services/                   # Business-Logik
├── infrastructure/
│   ├── db/
│   │   ├── models.py               # SQLAlchemy ORM
│   │   └── repositories/           # SQLAlchemy Implementierungen
│   └── realtime/
│       └── in_memory_event_bus.py  # In-Memory PubSub
└── tests/                          # pytest Tests
```

## Datenmodell

| Tabelle | Zweck |
|---------|-------|
| `conversations` | Direct Conversations (unique participantPairKey) |
| `conversation_participants` | Teilnehmer (unique conversationId + userId) |
| `messages` | Nachrichten (indexed conversationId + createdAt) |
| `read_states` | Letzter Read-State pro User/Conversation |

## API

### REST

| Endpoint | Zweck |
|----------|-------|
| `GET /health` | Liveness |
| `GET /health/live` | Liveness |
| `GET /health/ready` | Readiness (inkl. DB-Prüfung) |

### GraphQL

| Operation | Beschreibung |
|-----------|-------------|
| `query { conversations(userId) }` | Alle Conversations eines Users |
| `query { conversation(id, userId) }` | Einzelne Conversation |
| `query { messages(conversationId, userId, limit, before) }` | Message History |
| `mutation { createDirectConversation(userAId, userBId) }` | Direct Chat erstellen |
| `mutation { sendMessage(conversationId, senderId, body) }` | Nachricht senden |
| `mutation { markRead(conversationId, userId) }` | Als gelesen markieren |
| `subscription { messageReceived(userId) }` | Live-Empfang von Nachrichten |

## Schnellstart

### 1. PostgreSQL starten

```bash
docker compose -f compose.yaml up -d chat-postgres
```

### 2. Migrationen ausführen

```bash
uv sync
uv run alembic upgrade head
```

### 3. Service starten

```bash
uv run chat
```

Der Service läuft auf `http://localhost:8001`.

### 4. GraphQL Playground

`http://localhost:8001/graphql` – integrierte Strawberry Sandbox.

## Testanleitung (Two-Person-Realtime)

### Terminal 1 – Service

```bash
uv run chat
```

### Terminal 2 – Caleb subscribed

Öffne WebSocket-Verbindung zu `ws://localhost:8001/graphql` mit Subprotocol `graphql-transport-ws`:

```json
→ {"type": "connection_init"}
← {"type": "connection_ack"}
→ {"type": "subscribe", "id": "1", "payload": {"query": "subscription { messageReceived(userId: \"caleb\") { body senderId } }"}}
```

### Terminal 3 – Rachel subscribed

Gleicher WebSocket, gleiche Subscription mit `userId: "rachel"`.

### Terminal 4 – Senden

```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { createDirectConversation(userAId: \"caleb\", userBId: \"rachel\") { id } }"}'
```

`conversationId` aus der Response kopieren und:

```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { sendMessage(conversationId: \"<id>\", senderId: \"caleb\", body: \"Hallo Rachel\") { id body } }"}'
```

### Erwartung

- Caleb UND Rachel sehen die Nachricht sofort in ihren WebSocket-Clients
- Beide ohne Reload
- Validierung über `GET /health/ready`

## Automatisierter Test

```bash
uv run pytest -v
```

## Automatisierte Demo

```bash
python scripts/realtime_demo.py
```

## Einschränkungen (V1)

| Bereich | Einschränkung | Geplant |
|---------|---------------|---------|
| **Authentifizierung** | userId wird direkt übergeben, kein JWT | Keycloak-Integration |
| **EventBus** | In-Memory, nur single-process | Valkey/Redis PubSub |
| **Skalierung** | Kein Kubernetes / Multi-Replica Support | Redis PubSub + Stateless Design |
| **Gateway** | Keine Apollo Federation | GraphQL Federation |
| **Attachments** | Keine Datei-Uploads | S3/MinIO Integration |
| **Kafka** | Keine Outbound Events | Event-Driven Integration |
| **Frontend** | Noch kein UI-Chat | React/Vue Component |

## Bekannte Einschränkungen des In-Memory EventBus

- Funktioniert nur innerhalb einer Service-Instanz
- Bei mehreren Uvicorn/Hypercorn Workern oder Docker Replicas gehen Nachrichten verloren
- Muss durch Valkey/Redis PubSub ersetzt werden, sobald horizontal skaliert wird

## Nächste Schritte

1. JWT-Validierung (userId aus Token extrahieren)
2. Valkey/Redis PubSub als EventBus
3. Kafka-Outbound-Events für Notification-Service-Integration
4. Apollo Federation (als Subgraph ins bestehende Gateway)
5. Frontend-Komponente (React + Apollo Client)
6. Group Conversations
7. Attachments
