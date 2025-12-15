from rest_framework import serializers
from .models import ChatGroup, Message
from users.serializers import UserSerializer

class ChatGroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(source='member_count', read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'description', 'is_public', 'is_private', 'members', 'member_count']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'timestamp']