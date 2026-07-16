import strawberry
from strawberry import federation

from chat.api.graphql.mutations.conversation_mutation import ConversationMutation
from chat.api.graphql.mutations.message_mutation import MessageMutation
from chat.api.graphql.queries.conversation_query import ConversationQuery
from chat.api.graphql.queries.message_query import MessageQuery
from chat.api.graphql.subscriptions.message_subscription import MessageSubscription


@strawberry.type
class Query(ConversationQuery, MessageQuery):
    pass


@strawberry.type
class Mutation(ConversationMutation, MessageMutation):
    pass


@strawberry.type
class Subscription(MessageSubscription):
    pass


schema = federation.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    federation_version="2.11",
)
