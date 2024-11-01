from rest_framework import serializers


class AssistantSerializer(serializers.Serializer):
    query = serializers.CharField()
    include_external_data = serializers.BooleanField(default=False)
