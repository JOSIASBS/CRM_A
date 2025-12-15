from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, logout_view
from . import views

app_name = "users"

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path("", login_view, name="login"),
    path("login/", login_view, name="login"),
    path("fichar/", views.fichar, name="fichar"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.perfil_editar, name="perfil_editar"),
    path("logout/", logout_view, name="logout"),
    path("perfil/password/", views.cambiar_password, name="cambiar_password"),

    # Empleados
    path("empleados/", views.empleados_list, name="empleados_list"),
    path("empleados/<int:empleado_id>/", views.empleado_detail, name="empleado_detail"),

    # Departamentos
    path("departamentos/", views.departamentos_list, name="departamentos"),
    path("departamentos/<int:departamento_id>/", views.departamento_detail, name="departamento_detail"),

    # API
    path("api/", include(router.urls)),
]
