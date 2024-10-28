from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from core.serializer import MessageSerializer
from core.models import Conversation

from .assistant import QuantumAssistantConversation
from .serializer import AssistantSerializer

class AssistantView(APIView):

    def post(self, request, conversation_id):
        serial = AssistantSerializer(data=request.data)
        serial.is_valid(raise_exception=True)

        try:
            conversation = QuantumAssistantConversation(request.user, conversation_id)
            messages = conversation.process_query(serial.validated_data['query'], serial.validated_data['include_external_data'])

            # Only first and last message actually container question and answer. 
            # Intermediate messages can be follow up questions.
            message_serializer = MessageSerializer([messages[0], messages[-1]], many=True)

            return Response(data=message_serializer.data)
        except Conversation.DoesNotExist:
            raise NotFound('Conversation not found!')
