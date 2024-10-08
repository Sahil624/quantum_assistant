# quantum_assistant/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from .assistant import QuantumAssistantConversation

class QuantumAssistantConsumer(WebsocketConsumer):
    
    def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
        self.user = self.scope['user']
        self.conversation = QuantumAssistantConversation(self.user, self.conversation_id)

        if not self.conversation_id:
            self.conversation_id = self.conversation.conversation_obj.id
        self.conversation_group_name = f'conversation_{self.conversation_id}'

        # Join room group
        self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        self.accept()


        packet = {
            'type': 'conversation_acknowledge',
            'message': self.conversation_id
        }
        self.channel_layer.group_send(
            self.conversation_group_name,
            packet
        )

        print("===========> sent conversation ID", packet)




    def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Process the message
        response = self.process_message(message)
        packet = {
            'type': 'assistant_message',
            'message': response
        }
        # Send message to room group
        self.channel_layer.group_send(
            self.conversation_group_name,
            packet
        )

        self.assistant_message(packet)

    def assistant_message(self, event):
        # message = event['message']

        print("MESSAGE ASSISTANT", event)
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def process_message(self, message):
        return self.conversation.process_query(message)

    # Add a method for preemptive messaging (to be implemented in the future)
    def send_preemptive_message(self, message):
        self.send(text_data=json.dumps({
            'message': message,
            'type': 'preemptive'
        }))