"""
Realtime Chat Demo – End-to-End Test mit zwei WebSocket Clients.

Verwendung:
    python scripts/realtime_demo.py <url>

    url: GraphQL-Endpoint (default: http://localhost:8001/graphql)

Ablauf:
    1. WS Client A (caleb) subscribed to conversationUpdated(userId: "caleb")
    2. WS Client B (rachel) subscribed to conversationUpdated(userId: "rachel")
    3. REST: createDirectConversation(caleb, rachel)
    4. REST: sendMessage(caleb -> rachel)
    5. Prüfung: beide Clients erhalten Message live
"""
import asyncio
import json
import sys
import uuid

from httpx import AsyncClient
from websockets.asyncio.client import connect as ws_connect

GRAPHQL_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/graphql"
WS_URL = GRAPHQL_URL.replace("http://", "ws://").replace("https://", "wss://")


def make_ws_message(msg_type: str, payload: dict | None = None, id: str | None = None) -> str:
    msg: dict = {"type": msg_type}
    if id is not None:
        msg["id"] = id
    if payload is not None:
        msg["payload"] = payload
    return json.dumps(msg)


async def graphql_query(client: AsyncClient, query: str) -> dict:
    resp = await client.post(GRAPHQL_URL, json={"query": query})
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        print(f"  ERROR: {data['errors']}")
        sys.exit(1)
    return data["data"]


async def subscribe_user(user_id: str, results: list, ready: asyncio.Event):
    async with ws_connect(
        WS_URL,
        subprotocols=["graphql-transport-ws"],
        close_timeout=5,
    ) as ws:
        await ws.send(make_ws_message("connection_init", {}))
        ack = await ws.recv()
        ack_data = json.loads(ack)
        assert ack_data["type"] == "connection_ack", (
            f"Expected connection_ack, got {ack_data}"
        )

        sub_id = str(uuid.uuid4())
        sub_query = (
            f"subscription {{ conversationUpdated(userId: \"{user_id}\") "
            "{ id lastMessage lastMessageAt unreadCount } }"
        )
        sub_payload = {"query": sub_query}
        await ws.send(make_ws_message("subscribe", payload=sub_payload, id=sub_id))

        ready.set()

        while True:
            raw = await ws.recv()
            msg = json.loads(raw)
            if msg["type"] == "next" and msg["id"] == sub_id:
                payload = msg["payload"]["data"]["conversationUpdated"]
                print(f"  [{user_id}] RECEIVED via WS: {payload}")
                results.append(payload)
            elif msg["type"] == "complete":
                break


async def main():
    print("=" * 60)
    print("Omnixys Chat – Realtime Demo")
    print("=" * 60)
    print()

    async with AsyncClient() as client:
        print("[1/4] Caleb subscribed to conversationUpdated(userId: caleb)")
        caleb_results: list = []
        caleb_ready = asyncio.Event()
        caleb_task = asyncio.create_task(
            subscribe_user("caleb", caleb_results, caleb_ready)
        )

        print("[2/4] Rachel subscribed to conversationUpdated(userId: rachel)")
        rachel_results: list = []
        rachel_ready = asyncio.Event()
        rachel_task = asyncio.create_task(
            subscribe_user("rachel", rachel_results, rachel_ready)
        )

        await asyncio.wait_for(
            asyncio.gather(
                asyncio.create_task(caleb_ready.wait()),
                asyncio.create_task(rachel_ready.wait()),
            ),
            timeout=10.0,
        )
        print("  Both clients subscribed successfully")
        print()

        print("[3/4] Creating direct conversation caleb <-> rachel...")
        create_conv = (
            'mutation { createDirectConversation('
            'userAId: "caleb", userBId: "rachel"'
            ') { id participants { userId } } }'
        )
        data = await graphql_query(client, create_conv)
        conv_id = data["createDirectConversation"]["id"]
        print(f"  Conversation ID: {conv_id}")
        print(f"  Participants: {data['createDirectConversation']['participants']}")
        print()

        print("[4/4] Sending message from caleb to rachel...")
        send_msg = (
            f'mutation {{ sendMessage(conversationId: "{conv_id}"'
            ', senderId: "caleb"'
            ', body: "Hallo Rachel, live von GraphQL Subscription!"'
            ") { id body } }"
        )
        data = await graphql_query(client, send_msg)
        msg_id = data["sendMessage"]["id"]
        print(f"  Message ID: {msg_id}")
        print()

        await asyncio.sleep(2.0)

        caleb_task.cancel()
        rachel_task.cancel()
        for t in [caleb_task, rachel_task]:
            try:
                await t
            except asyncio.CancelledError:
                pass

        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)

        caleb_received = len(caleb_results) > 0
        rachel_received = len(rachel_results) > 0

        if caleb_received:
            print(f"  Caleb received: {caleb_results[0]}")
        else:
            print("  Caleb received: NOTHING (FAIL)")

        if rachel_received:
            print(f"  Rachel received: {rachel_results[0]}")
        else:
            print("  Rachel received: NOTHING (FAIL)")

        print()
        if caleb_received and rachel_received:
            print("  >>> PASS: Beide User erhalten Nachrichten live via GraphQL Subscription")
        else:
            print("  >>> FAIL: Realtime Delivery fehlgeschlagen")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
