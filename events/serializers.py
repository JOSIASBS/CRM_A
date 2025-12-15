from rest_framework import serializers
from .models import Solicitud, Evento

class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = [
            'id',
            'user',
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'descripcion',
            'estado',
            'created_at',
            'reviewed_by'
        ]
        read_only_fields = [
            'user',
            'estado',
            'created_at',
            'reviewed_by'
        ]

class EventoSerializer(serializers.ModelSerializer):
    # Campos para FullCalendar (lectura)
    title = serializers.CharField(source="titulo", read_only=True)
    start = serializers.DateTimeField(source="inicio", read_only=True)
    end = serializers.DateTimeField(source="fin", read_only=True)

    class Meta:
        model = Evento
        fields = [
            "id",

            # FullCalendar
            "title",
            "start",
            "end",

            # Modelo real (escritura)
            "titulo",
            "tipo",
            "descripcion",
            "inicio",
            "fin",

            "user",
        ]
        read_only_fields = ["user"]