from django.contrib import admin
from .models import AIInteraction, ActivityLog, AssignmentSubmission, Course, LearningObject

class LearningObjectInline(admin.TabularInline):
    model = LearningObject
    extra = 1  # Number of empty forms to display
    fields = ('object_id', 'order')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'learning_object_count')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [LearningObjectInline]

    def learning_object_count(self, obj):
        return obj.learning_objects.count()
    learning_object_count.short_description = 'Learning Objects'

@admin.register(LearningObject)
class LearningObjectAdmin(admin.ModelAdmin):
    list_display = ('object_id', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('object_id', 'course__title')
    ordering = ('course', 'order')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'learning_object', 'activity_type', 'timestamp')
    list_filter = ('activity_type', 'timestamp', 'course')
    search_fields = ('user__username', 'course__title', 'learning_object__object_id')
    date_hierarchy = 'timestamp'

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_object', 'submitted_at', 'score')
    list_filter = ('submitted_at', 'score')
    search_fields = ('user__username', 'learning_object__object_id')
    date_hierarchy = 'submitted_at'

@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'learning_object', 'timestamp', 'helpfulness_rating')
    list_filter = ('timestamp', 'helpfulness_rating', 'course')
    search_fields = ('user__username', 'course__title', 'question', 'answer')
    date_hierarchy = 'timestamp'