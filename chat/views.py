from rest_framework import viewsets,permissions,status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from django.db import models


class ChatGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatGroup.objects.all()
    serializer_class = ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # mostrar grupos públicos + grupos donde es miembro
        return ChatGroup.objects.filter(models.Q(is_public=True) | models.Q(members=user)).distinct()

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        group_id = self.request.query_params.get('group')
        qs = Message.objects.none()
        if group_id:
            group = get_object_or_404(ChatGroup, id=group_id)
            # permitir ver si es public o miembro
            if group.is_public or user in group.members.all():
                qs = Message.objects.filter(group=group).order_by('timestamp')
        return qs

# Django views to render templates (sync)
@login_required
def chat_groups_list(request):
    user = request.user

    grupos = ChatGroup.objects.filter(
        is_private=False,
        members=user
    ).exclude(name__iexact="anuncios").distinct()

    privados = ChatGroup.objects.filter(
        is_private=True,
        members=user
    )

    anuncios = ChatGroup.objects.filter(
        is_public=True,
        name__iexact='anuncios'
    ).first()

    return render(request, "chat/chat_groups_list.html", {
        "grupos": grupos,
        "privados": privados,
        "obtener_grupo_anuncios": anuncios,
        "empleado": user,
    })



@login_required
def chat_group_detail(request, group_id):
    user = request.user
    grupo = get_object_or_404(ChatGroup, id=group_id)
    # security: only allow view if public or member
    if not grupo.is_public and user not in grupo.members.all():
        return redirect("chat:chat_groups_list")
    mensajes = Message.objects.filter(group=grupo).order_by('timestamp')
    solo = grupo.members.count() <= 1
    puede_enviar = grupo.is_public is False and user not in grupo.members.all() == False
    # form handled via POST below or via websocket; to keep older templates, allow POST
    if request.method == "POST":
        content = request.POST.get("content","").strip()
        if content:
            Message.objects.create(group=grupo, sender=user, content=content)
            return redirect("chat:chat_group_detail", group_id=group_id)


    return render(request, "chat/chat_group_detail.html", {
        "grupo": grupo,
        "mensajes": mensajes,
        "puede_enviar": (user.role in ['admin','manager']) if grupo.name.lower()=='anuncios' else (user in grupo.members.all() or grupo.is_public),
        "form": None,
        "empleado": user,
        "solo_en_grupo": solo,

    })

@login_required
def private_chat(request, other_id):
    user = request.user
    other = get_object_or_404(CustomUser, id=other_id)
    # find or create a private ChatGroup with exactly these two members
    grupo = ChatGroup.objects.filter(is_private=True, members=user).filter(members=other).distinct().first()
    if not grupo:
        grupo = ChatGroup.objects.create(name=f"Privado: {user.username} & {other.username}", is_private=True)
        grupo.members.add(user, other)
    mensajes = Message.objects.filter(group=grupo).order_by('timestamp')
    if request.method == "POST":
        content = request.POST.get("content","").strip()
        if content:
            Message.objects.create(group=grupo, sender=user, content=content)
            return redirect("chat:private_chat", other_id=other_id)
    return render(request, "chat/private_chat.html", {
        "other": other,
        "mensajes": mensajes,
        "puede_enviar": True,
        "form": None,
        "empleado": user,
    })

@login_required
def crear_chat(request):
    user = request.user
    usuarios = CustomUser.objects.exclude(id=user.id)

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        nombre = request.POST.get("name", "").strip()
        miembros_ids = request.POST.getlist("members")

        # 🔴 VALIDACIÓN CHAT PRIVADO
        if tipo == "private":
            if len(miembros_ids) != 1:
                return render(request, "chat/crear_chat.html", {
                    "usuarios": usuarios,
                    "empleado": user,
                    "error": "Un chat privado debe tener exactamente un miembro",
                    "tipo": tipo,
                    "nombre": nombre,
                    "miembros_seleccionados": miembros_ids,
                })

            other = get_object_or_404(CustomUser, id=miembros_ids[0])

            grupo = ChatGroup.objects.filter(
                is_private=True,
                members=user
            ).filter(members=other).first()

            if not grupo:
                grupo = ChatGroup.objects.create(
                    name="",
                    is_private=True
                )
                grupo.members.add(user, other)

            return redirect("chat:private_chat", other_id=other.id)

        # 🔴 VALIDACIÓN CHAT GRUPAL
        if tipo == "group":
            if not nombre:
                return render(request, "chat/crear_chat.html", {
                    "usuarios": usuarios,
                    "empleado": user,
                    "error": "El grupo debe tener nombre",
                    "tipo": tipo,
                    "nombre": nombre,
                    "miembros_seleccionados": miembros_ids,
                })

            grupo = ChatGroup.objects.create(
                name=nombre,
                is_private=False
            )
            grupo.members.add(user)

            for uid in miembros_ids:
                grupo.members.add(uid)

            return redirect("chat:chat_group_detail", group_id=grupo.id)

    return render(request, "chat/crear_chat.html", {
        "usuarios": usuarios,
        "empleado": user,
    })


@login_required
def salir_grupo(request, group_id):
    user = request.user
    grupo = get_object_or_404(ChatGroup, id=group_id)

    if user in grupo.members.all():
        if grupo.name.lower() == "anuncios":
            return redirect("chat:chat_group_detail", group_id=group_id)
        grupo.members.remove(user)

    return redirect("chat:chat_groups_list")
