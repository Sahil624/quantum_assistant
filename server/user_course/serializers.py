import logging
from rest_framework import serializers

from common.exceptions import CellMetaDataNotFoundError

from .metastore import get_cell_meta
from .models import (
    AIInteraction,
    ActivityLog,
    AssignmentSubmission,
    Course,
    LearningObject,
)
from django.db import transaction


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "course",
            "learning_object",
            "activity_type",
            "timestamp",
            "duration",
            "details",
        ]
        read_only_fields = ["id", "timestamp", "user"]


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "user",
            "learning_object",
            "submitted_at",
            "score",
            "feedback",
        ]
        read_only_fields = ["id", "submitted_at"]


class AIInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInteraction
        fields = [
            "id",
            "user",
            "course",
            "learning_object",
            "question",
            "answer",
            "timestamp",
            "helpfulness_rating",
        ]
        read_only_fields = ["id", "timestamp"]


class LearningObjectSerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        try:
            return get_cell_meta(obj.object_id)
        except CellMetaDataNotFoundError as e:
            logging.error(f"Could not find meta data. Setting None. [Message={str(e)}]")
            return None

    class Meta:
        model = LearningObject
        exclude = []
        read_only_fields = ["id", "object_id", "course", "order", "metadata"]


class CourseSerializer(serializers.ModelSerializer):
    learning_objects = LearningObjectSerializer(many=True, read_only=True)
    learning_object_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "user",
            "learning_objects",
            "learning_object_ids",
        ]

    def create(self, validated_data):
        learning_object_ids = validated_data.pop("learning_object_ids", [])

        # if learning_object_ids:
        #     lo_set = set(learning_object_ids)

        #     for lo in learning_object_ids:
        #         lo_set.add(lo)
        #         try:
        #             meta_data = get_cell_meta(lo)
        #             lo_set.update(meta_data["cell_prereqs"])

        #         except CellMetaDataNotFoundError:
        #             pass

        #     learning_object_ids = list(lo_set)

        unique_los = []

        for x in learning_object_ids:
            if x not in unique_los:
                unique_los.append(x)

        course = Course.save_course_and_learning_objects(
            user=self.context["request"].user,
            title=validated_data["title"],
            description=validated_data.get("description", ""),
            learning_object_ids=unique_los,
        )
        return course

    def update(self, instance, validated_data):
        learning_object_ids = validated_data.pop("learning_object_ids", None)

        # Update course fields
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        # Update learning objects if provided
        if learning_object_ids is not None:
            with transaction.atomic():
                current_los = list(instance.learning_objects.all())
                current_lo_ids = [lo.object_id for lo in current_los]

                # Identify new, removed, and existing LOs
                new_lo_ids = set(learning_object_ids) - set(current_lo_ids)
                removed_lo_ids = set(current_lo_ids) - set(learning_object_ids)
                existing_lo_ids = set(current_lo_ids) & set(learning_object_ids)

                # Remove LOs not in the new list
                instance.learning_objects.filter(object_id__in=removed_lo_ids).delete()

                # Add new LOs
                for object_id in new_lo_ids:
                    LearningObject.objects.create(
                        course=instance,
                        object_id=object_id,
                        order=learning_object_ids.index(object_id),
                    )

                # Update order of existing LOs
                for lo in instance.learning_objects.filter(
                    object_id__in=existing_lo_ids
                ):
                    lo.order = learning_object_ids.index(lo.object_id)
                    lo.save()

        return instance


class CellDataSerializer(serializers.Serializer):
    interactive = serializers.BooleanField(default=False)
    content = serializers.CharField(required=False)
    redirect_link = serializers.URLField(required=False)
    quiz_cell = serializers.CharField(required=False)
