from django.db import models
from django.conf import settings

class ChatGroup(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)   # anuncios, visible a todos
    is_private = models.BooleanField(default=False)  # si True, sólo miembros pueden ver/participar
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class Message(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} @ {self.group}: {self.content[:30]}"