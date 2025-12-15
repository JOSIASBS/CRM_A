
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
)

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    fecha_contratacion = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def initials(self):
        if self.first_name or self.last_name:
            return (self.first_name[:1] + (self.last_name[:1] if self.last_name else '')).upper()
        return self.username[:1].upper()


class Punch(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='punches')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start']

    @property
    def is_open(self):
        return self.end is None

    def close(self):
        if self.end is None:
            self.end = timezone.now()
            self.save()