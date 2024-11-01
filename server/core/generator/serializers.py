from rest_framework import serializers

class CourseSerializer(serializers.Serializer):
    learning_object_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    total_time = serializers.IntegerField()

    optimized_learning_object_ids = serializers.ListField(
         child=serializers.CharField(), read_only=True
    )