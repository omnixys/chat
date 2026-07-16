# Chat Service V1

The Chat Service provides authenticated realtime chat over GraphQL HTTP and
`graphql-transport-ws`.

- In-app conversations connect two registered users.
- WhatsApp conversations connect the authenticated app user with one normalized
  external E.164 phone number.
- Public operations derive the user and sender from the Keycloak principal.
- Conversation membership is checked for queries, mutations and subscriptions.
- The conversation fixes the channel; a client cannot select it per message.
- WhatsApp text is sent through the Communication Gateway. Inbound Evolution
  messages are matched only to an existing external-number conversation.
- Provider IDs are unique and repeated webhooks do not create duplicate messages.
- Realtime events use Valkey Pub/Sub; PostgreSQL remains the offline history.

V1 intentionally has no media, groups, reactions, typing indicators, presence,
email/SMS chat or automatic channel fallback.
