from django.contrib import admin
from .models import SystemPrompt, Conversation, Message, AIResponse, PerformanceMetric

@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('assistant_type', 'version', 'is_active', 'created_at')
    list_filter = ('assistant_type', 'is_active')
    search_fields = ('assistant_type', 'version', 'content')
    ordering = ('-created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'system_prompt', 'title', 'created_at', 'updated_at')
    list_filter = ('system_prompt__assistant_type', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'system_prompt__assistant_type')
    ordering = ('-updated_at',)
    raw_id_fields = ('user', 'system_prompt')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'system_prompt')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'message_type', 'is_original_user_query', 'is_out_of_context_message', 'is_answer', 'timestamp')
    list_filter = ('message_type', 'is_answer', 'is_original_user_query', 'timestamp')
    search_fields = ('content', 'conversation__title')
    ordering = ('-timestamp',)
    raw_id_fields = ('conversation',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation')

@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'ai_type', 'attempt_number', 'is_final_answer', 'timestamp')
    list_filter = ('ai_type', 'is_final_answer', 'timestamp')
    search_fields = ('response_content', 'message__content')
    ordering = ('-timestamp',)
    raw_id_fields = ('message',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('message')

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'metric_name', 'metric_value', 'timestamp')
    list_filter = ('metric_name', 'timestamp')
    search_fields = ('metric_name', 'conversation__title')
    ordering = ('-timestamp',)
    raw_id_fields = ('conversation',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation')