from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# no registramos viewsets de momento o puedes registrarlos si quieres la API

app_name = "chat"

urlpatterns = [
    path("", views.chat_groups_list, name="chat_groups_list"),
    path("crear/", views.crear_chat, name="crear_chat"),
    path("grupo/<int:group_id>/", views.chat_group_detail, name="chat_group_detail"),
    path("private/<int:other_id>/", views.private_chat, name="private_chat"),
    path("salir/<int:group_id>/", views.salir_grupo, name="salir_grupo"),

    path("api/", include(router.urls)),
]