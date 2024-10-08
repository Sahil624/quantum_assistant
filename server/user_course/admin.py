from django.contrib import admin
from .models import Course, LearningObject

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