from django.db import models
from django.contrib.auth import get_user_model

class SystemPrompt(models.Model):
    ASSISTANT_TYPES = [
        ('STUDY', 'Study Assistant'),
        ('COURSE', 'Course Generator'),
    ]
    
    assistant_type = models.CharField(max_length=10, choices=ASSISTANT_TYPES)
    version = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    # New fields
    description = models.TextField(blank=True, help_text="Brief description of changes in this version")
    performance_metrics = models.JSONField(null=True, blank=True, help_text="Stores performance metrics for this prompt")

    class Meta:
        unique_together = ['assistant_type', 'version']

    def __str__(self):
        return f"{self.get_assistant_type_display()} - v{self.version}"

class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    system_prompt = models.ForeignKey(SystemPrompt, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New fields
    context = models.TextField(blank=True, help_text="Any additional context for the conversation")
    tags = models.JSONField(null=True, blank=True, help_text="Custom tags for categorizing conversations")
    user_feedback = models.IntegerField(null=True, blank=True, help_text="User rating for the conversation (e.g., 1-5)")
    
    def __str__(self):
        return f"{self.title} - {self.user.username} with {self.system_prompt}"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('USER', 'User'),
        ('ASSISTANT', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_answer = models.BooleanField(default=False)
    
    # New fields
    tokens = models.IntegerField(null=True, help_text="Number of tokens in the message")
    sentiment = models.FloatField(null=True, help_text="Sentiment score of the message")
    entities = models.JSONField(null=True, blank=True, help_text="Named entities extracted from the message")

    def __str__(self):
        return f"{self.get_message_type_display()} message in {self.conversation.title}"

class AIResponse(models.Model):
    AI_TYPES = [
        ('LOCAL', 'Local Model'),
        ('CLAUDE', 'Claude Model'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='ai_responses')
    ai_type = models.CharField(max_length=10, choices=AI_TYPES)
    attempt_number = models.PositiveSmallIntegerField()
    response_content = models.TextField()
    is_final_answer = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # New fields
    processing_time = models.FloatField(null=True, help_text="Time taken to generate the response in seconds")
    confidence_score = models.FloatField(null=True, help_text="Model's confidence in the response")
    used_resources = models.JSONField(null=True, blank=True, help_text="Resources or knowledge bases used for the response")

    class Meta:
        unique_together = ['message', 'ai_type', 'attempt_number']

    def __str__(self):
        return f"{self.get_ai_type_display()} response (Attempt {self.attempt_number}) for Message {self.message.id}"

class PerformanceMetric(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name} for Conversation {self.conversation.id}"