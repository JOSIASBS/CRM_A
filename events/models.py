from django.db import models
from django.conf import settings

TIPOS = (
    ('vacaciones', 'Vacaciones'),
    ('permiso', 'Permiso'),
    ('otro', 'Otro'),
)

class Solicitud(models.Model):

    ESTADOS = (
        ('en_espera', 'En espera'),
        ('aprobado', 'Aprobado'),
        ('denegado', 'Denegado'),
    )

    TIPOS = (
        ('vacaciones', 'Vacaciones'),
        ('permiso', 'Permiso'),
        ('otro', 'Otro'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    descripcion = models.TextField(blank=True)

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='en_espera'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='solicitudes_revisadas'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tipo} - {self.estado}"

class Evento(models.Model):

    TIPOS = (
        ('reunion', 'Reunión'),
        ('otro', 'Otro'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eventos",
        null=True,
        blank=True
    )
    # user = None → evento global (admin)

    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    inicio = models.DateTimeField()
    fin = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo