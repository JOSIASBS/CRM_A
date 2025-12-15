from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import CustomUser, Punch, Department
from .serializers import UserSerializer
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import PerfilForm


# ---------------------------
# PERMISOS API
# ---------------------------

class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "manager"]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return CustomUser.objects.all()
        elif user.role == "manager":
            return CustomUser.objects.filter(department=user.department)
        else:
            return CustomUser.objects.filter(id=user.id)


# ---------------------------
# LOGIN
# ---------------------------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("users:fichar")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "users/login.html")


# ---------------------------
# FICHAR / PUNCH CLOCK
# ---------------------------

@login_required
def fichar(request):
    user = request.user
    hoy = timezone.localdate()

    fichaje_hoy = Punch.objects.filter(
        user=user,
        start__date=hoy,
        end__isnull=True
    ).first()

    # Entrada
    if request.method == "POST" and "entrada" in request.POST:
        if fichaje_hoy:
            messages.error(request, "Ya has fichado hoy.")
        else:
            Punch.objects.create(user=user)
            messages.success(request, "Entrada registrada.")
        return redirect("users:fichar")

    # Salida
    if request.method == "POST" and "salida" in request.POST:
        if fichaje_hoy and fichaje_hoy.end is None:
            fichaje_hoy.end = timezone.now()
            fichaje_hoy.save()
            messages.success(request, "Salida registrada.")
        else:
            messages.error(request, "No tienes una entrada abierta.")
        return redirect("users:fichar")

    historial = []
    for p in Punch.objects.filter(user=user):
        historial.append({
            "fecha": p.start.date(),
            "hora_entrada": p.start.time().strftime("%H:%M:%S"),
            "hora_salida": p.end.time().strftime("%H:%M:%S") if p.end else None
        })

    return render(request, "users/fichar.html", {
        "empleado": user,  # ahora el empleado es el CustomUser
        "fichaje_hoy": fichaje_hoy,
        "fichajes": historial,
    })


# ---------------------------
# PERFIL
# ---------------------------

@login_required
def perfil(request):
    return render(request, "users/perfil.html", {"user": request.user})


# ---------------------------
# LISTA DE EMPLEADOS
# ---------------------------

@login_required
def empleados_list(request):
    user = request.user

    # ADMIN ve todos, MANAGER solo su departamento
    if user.role == "admin":
        empleados = CustomUser.objects.all()
        departamentos = Department.objects.all()
    elif user.role == "manager":
        empleados = CustomUser.objects.filter(department=user.department)
        departamentos = None
    else:
        messages.error(request, "No tienes acceso a este apartado.")
        return redirect("users:fichar")

    # Filtros
    nombre = request.GET.get("nombre")
    fecha = request.GET.get("fecha")
    departamento = request.GET.get("departamento")

    if nombre:
        empleados = empleados.filter(
            username__icontains=nombre
        ) | empleados.filter(
            first_name__icontains=nombre
        ) | empleados.filter(
            last_name__icontains=nombre
        )

    if fecha:
        empleados = empleados.filter(fecha_contratacion=fecha)

    if departamento and user.role == "admin":
        empleados = empleados.filter(department_id=departamento)

    return render(request, "users/empleados_list.html", {
        "empleados": empleados,
        "departamentos": departamentos,
        "is_admin": user.role == "admin",
        "empleado": user,
    })



# ---------------------------
# DETALLE EMPLEADO
# ---------------------------

@login_required
def empleado_detail(request, empleado_id):
    empleado = get_object_or_404(CustomUser, id=empleado_id)

    fichajes = []
    for p in Punch.objects.filter(user=empleado):
        fichajes.append({
            "fecha": p.start.date(),
            "hora_entrada": p.start.time().strftime("%H:%M:%S"),
            "hora_salida": p.end.time().strftime("%H:%M:%S") if p.end else None
        })

    return render(request, "users/empleado_detail.html", {
        "empleado": empleado,
        "fichajes": fichajes,
    })

# ---------------------------
# DEPARTAMENTOS
# ---------------------------

@login_required
def departamentos_list(request):
    user = request.user

    if user.role == "employee":
        messages.error(request, "No tienes acceso a los departamentos.")
        return redirect("users:fichar")

    # ADMIN
    if user.role == "admin":
        departamentos = Department.objects.all()

    # MANAGER
    else:
        departamentos = Department.objects.filter(id=user.department_id)

    return render(request, "users/departamentos_list.html", {
        "departamentos": departamentos,
        "empleado": user,
    })



@login_required
def departamento_detail(request, departamento_id):
    user = request.user
    departamento = get_object_or_404(Department, id=departamento_id)

    # EMPLOYEE → fuera
    if user.role == "employee":
        messages.error(request, "No tienes acceso a este apartado.")
        return redirect("users:fichar")

    # MANAGER → solo su departamento
    if user.role == "manager" and user.department != departamento:
        messages.error(request, "No puedes acceder a otros departamentos.")
        return redirect("users:departamentos")

    empleados = departamento.employees.all()

    conectados = empleados.filter(
        last_login__gte=timezone.now() - timezone.timedelta(minutes=10)
    ).count()

    # ADMIN
    if user.role == "admin":
        return render(request, "users/departamentos_manager.html", {
            "departamento": departamento,
            "empleados": empleados,
            "conectados": conectados,
            "total_empleados": empleados.count(),
            "empleado": user,
        })

    # MANAGER
    return render(request, "users/departamentos_manager.html", {
        "departamento": departamento,
        "empleados": empleados,
        "conectados": conectados,
        "total_empleados": empleados.count(),
        "empleado": user,
    })


# ---------------------------
# EDITAR PERFIL
# ---------------------------

@login_required
def perfil_editar(request):
    user = request.user

    if request.method == "POST":
        perfil_form = PerfilForm(request.POST, request.FILES, instance=user)

        if perfil_form.is_valid():
            perfil_form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("users:perfil")
    else:
        perfil_form = PerfilForm(instance=user)

    return render(request, "users/perfil_editar.html", {
        "perfil_form": perfil_form,
        "empleado": user,
    })



# ---------------------------
# DESLOGUEAR
# ---------------------------

def logout_view(request):
    logout(request)
    return redirect("users:login")



# ---------------------------
# CAMBIAR CONTRASEÑA
# ---------------------------
@login_required
def cambiar_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("users:perfil")
    else:
        form = PasswordChangeForm(request.user)

    # Traducción labels
    form.fields['old_password'].label = "Contraseña actual"
    form.fields['new_password1'].label = "Nueva contraseña"
    form.fields['new_password2'].label = "Repetir nueva contraseña"

    return render(request, "users/cambiar_password.html", {
        "form": form
    })
