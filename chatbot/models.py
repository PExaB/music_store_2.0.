from django.conf import settings
from django.db import models
from django.utils import timezone  # <-- добавьте этот импорт

class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(default=timezone.now)   # изменено
    updated_at = models.DateTimeField(default=timezone.now)   # изменено
    last_products = models.TextField(blank=True, null=True)  # хранит JSON последних товаров

    def __str__(self):
        return f"ChatSession {self.session_key}"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('function', 'Функция'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    function_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)   # изменено

    class Meta:
        ordering = ['created_at']