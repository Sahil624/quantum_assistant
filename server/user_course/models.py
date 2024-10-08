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
        course = Course.objects.create(
            user=user,
            title=title,
            description=description
        )
        
        for index, object_id in enumerate(learning_object_ids):
            LearningObject.objects.create(
                course=course,
                object_id=object_id,
                order=index
            )
        
        return course

class LearningObject(models.Model):
    object_id = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_objects')
    order = models.PositiveIntegerField()
    started_on = models.DateTimeField(blank=True, null=True)
    completed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = (('object_id', 'course'),)
