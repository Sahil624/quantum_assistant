from rest_framework import serializers
from django.db.models import Q

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            "content",
            "message_type",
            "timestamp",
            "is_answer",
            "is_original_user_query",
            "is_out_of_context_message",
            "entities",
        )


class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    assistant_type = serializers.CharField(write_only=True, required=False)
    system_prompt_type = serializers.CharField(
        source="system_prompt.assistant_type", read_only=True
    )

    class Meta:
        model = Conversation
        fields = (
            "id",
            "title",
            "created_at",
            "updated_at",
            "messages",
            "assistant_type",
            "system_prompt_type",
        )
        read_only_fields = ("system_prompt", "system_prompt_type")

    def get_messages(self, instance):
        # Check if this is a detail view
        if self.context.get("view").action == "retrieve":
            messages = instance.messages.filter(
                Q(is_original_user_query=True) | Q(is_answer=True) | Q(is_out_of_context_message=True)
            )
            serializer = MessageSerializer(messages, many=True)
            return serializer.data
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get("view").action != "retrieve":
            representation.pop("messages", None)
        return representation
