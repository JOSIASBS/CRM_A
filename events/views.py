from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Solicitud, Evento
from .serializers import SolicitudSerializer, EventoSerializer
from rest_framework.exceptions import PermissionDenied


# ---------------------------
# SOLICITUDES (HTML)
# ---------------------------

@login_required
def solicitudes(request):
    user = request.user

    if request.method == "POST":
        Solicitud.objects.create(
            user=user,
            tipo=request.POST.get("tipo"),
            fecha_inicio=request.POST.get("fecha_inicio"),
            fecha_fin=request.POST.get("fecha_fin"),
            descripcion=request.POST.get("descripcion"),
        )
        messages.success(request, "Solicitud enviada correctamente")
        return redirect("events:solicitudes")

    if user.role == "admin":
        solicitudes = Solicitud.objects.all().order_by("-created_at")
    elif user.role == "manager":
        solicitudes = Solicitud.objects.filter(
            user__department=user.department
        ).order_by("-created_at")
    else:
        solicitudes = Solicitud.objects.filter(user=user).order_by("-created_at")

    return render(request, "events/solicitudes.html", {
        "solicitudes": solicitudes,
        "empleado": user,
    })


@login_required
def aprobar_solicitud(request, solicitud_id, accion):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if request.user.role != "admin":
        messages.error(request, "No tienes permiso")
        return redirect("events:solicitudes")

    if accion == "aprobar":
        solicitud.estado = "aprobado"
    elif accion == "denegar":
        solicitud.estado = "denegado"

    solicitud.reviewed_by = request.user
    solicitud.save()

    return redirect("events:solicitudes")


# ---------------------------
# API SOLICITUDES
# ---------------------------

class SolicitudViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Solicitud.objects.all()
        return Solicitud.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------
# API EVENTOS (CALENDARIO)
# ---------------------------

from rest_framework.exceptions import PermissionDenied

class EventoViewSet(viewsets.ModelViewSet):
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Evento.objects.all()

        return Evento.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        )

    def perform_create(self, serializer):
        user = self.request.user
        is_global = self.request.data.get("global", False)

        if user.role == "admin" and is_global:
            serializer.save(user=None)
        else:
            serializer.save(user=user)


    def destroy(self, request, *args, **kwargs):
        evento = self.get_object()
        user = request.user


        if user.role == "admin":
            return super().destroy(request, *args, **kwargs)


        if evento.user == user:
            return super().destroy(request, *args, **kwargs)

        raise PermissionDenied("No tienes permiso para borrar este evento")



# ---------------------------
# CALENDARIO (HTML)
# ---------------------------

@login_required
def calendario(request):
    return render(request, "events/calendario.html", {
        "empleado": request.user
    })
