from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @staticmethod
    @transaction.atomic
    def save_course_and_learning_objects(user, title, description, learning_object_ids):
        course = Course.objects.create(user=user, title=title, description=description)

        for index, object_id in enumerate(learning_object_ids):
            print(object_id)
            LearningObject.objects.create(
                course=course, object_id=object_id, order=index
            )

        return course


class LearningObject(models.Model):
    object_id = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="learning_objects"
    )
    order = models.PositiveIntegerField()
    started_on = models.DateTimeField(blank=True, null=True)
    completed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["order"]
        unique_together = (("object_id", "course"),)


class ActivityLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    learning_object = models.ForeignKey(
        LearningObject, on_delete=models.CASCADE, null=True, blank=True
    )
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ("login", "Login"),
            ("view_content", "View Content"),
            ("complete_object", "Complete Learning Object"),
            ("ask_question", "Ask Question"),
            ("submit_assignment", "Submit Assignment"),
        ],
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)


class AssignmentSubmission(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)


class AIInteraction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    learning_object = models.ForeignKey(
        LearningObject, on_delete=models.CASCADE, null=True, blank=True
    )
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    helpfulness_rating = models.IntegerField(null=True, blank=True)
