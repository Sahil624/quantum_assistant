from rest_framework import viewsets, permissions, serializers

from core.models import Conversation, SystemPrompt
from core.serializer import ConversationSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        assistant_type = serializer.validated_data.pop("assistant_type", None)
        if assistant_type:
            system_prompt = SystemPrompt.objects.filter(
                assistant_type=assistant_type, is_active=True
            ).first()
            if not system_prompt:
                raise serializers.ValidationError(
                    f"No active system prompt found for assistant type: {assistant_type}"
                )
            serializer.save(user=self.request.user, system_prompt=system_prompt)
        else:
            raise serializers.ValidationError(
                "assistant_type is required for creating a conversation"
            )

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
