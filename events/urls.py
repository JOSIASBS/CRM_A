from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SolicitudViewSet,
    EventoViewSet,
    solicitudes,
    aprobar_solicitud,
    calendario,
)

app_name = "events"

router = DefaultRouter()
router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = [
    path("solicitudes/", solicitudes, name="solicitudes"),
    path(
        "solicitudes/<int:solicitud_id>/<str:accion>/",
        aprobar_solicitud,
        name="aprobar_solicitud"
    ),
    path("calendario/", calendario, name="calendario"),
    path("api/", include(router.urls)),
]
