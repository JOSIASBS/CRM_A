from rest_framework import serializers
from .models import CustomUser, Punch, Department
from events.models import Solicitud

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username','first_name','last_name','email','role','department','phone','address','avatar_url','initials']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            url = obj.avatar.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    class PunchSerializer(serializers.ModelSerializer):
        class Meta:
            model = Punch
            fields = ['id', 'start', 'end', 'is_open']
            read_only_fields = ['start', 'is_open']