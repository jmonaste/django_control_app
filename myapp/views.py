from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Project, Task, ChangeLog, ChangeReason, MotivoRechazo
from django.shortcuts import get_object_or_404, render, redirect
from .forms import createNewTask, createNewProject
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm, EmployeeTaskForm, TaskDeliveryClientForm, TaskUploadImage, TaskClientApprovalForm, TaskFormRechazoCliente, TaskFormRechazoManager, TaskFormRechazoCliente
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_user
from django.db.models import Q  # Import the Q object
from django.db.models import Count, Prefetch
import plotly.express as px
from django.db import connection


# Create your views here.


#region vistas generales

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@unauthenticated_user
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('index')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})

@unauthenticated_user
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('index')
    
@allowed_user(allowed_roles=['admin', 'manager', 'employee', 'customer'])
def signout(request):
    logout(request)
    return redirect('index')

#endregion

#region vistas proyecto
@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def projects(request):
    # projects = list(Project.objects.values())
    projects = Project.objects.all()
    # return JsonResponse(projects, safe=False)
    return render(request, 'projects/projects.html', {
        'projects': projects
    })

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def create_project(request):
    if request.method == 'GET':
        return render(request, 'projects/create_project.html', {
            'form': createNewProject()
        })
    else:
        project = Project.objects.create(name=request.POST["name"])
        return redirect('projects')

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    tasks = Task.objects.filter(project_id=id)
    print(project)
    return render(request, 'projects/detail.html', {
        'project': project,
        'tasks': tasks
    })

#endregion

# VISTAS TAREAS --------------------------------------------------------------------------------------------

#region Employee

@login_required
@allowed_user(allowed_roles=['admin', 'manager', 'employee'])
def tasks(request):
    tasks = Task.objects.filter(Q(employee_user=request.user), datecompleted__isnull=True)
    pending_tasks_count = Task.objects.filter(datecompleted__isnull=True).count() # se mostrará para admins y managers
    pending_tasks_per_user = Task.objects.filter(datecompleted__isnull=True).values('employee_user_id__username').annotate(total=Count('id')) # 
    
    # Obtener la descripción del motivo de rechazo para cada tarea
    for task in tasks:
        if task.motivo_rechazo_manager:
            motivo_rechazo_id = task.motivo_rechazo_manager
            motivo_rechazo_desc = MotivoRechazo.objects.get(codigo=motivo_rechazo_id).descripcion
            task.motivo_rechazo_desc = motivo_rechazo_desc  # Añadir el campo de descripción al objeto de tarea


    return render(request, 'tasks/tasks.html', {
        'tasks': tasks,
        'pending_tasks_count': pending_tasks_count,
        'pending_tasks_per_user': pending_tasks_per_user
    })

@login_required
def task_search(request):
    # filtramos las tareas por usuario, por pendiente y por id (patente)
    query = request.GET.get('q')
    tasks = Task.objects.filter(employee_user=request.user, datecompleted__isnull=True, vin__icontains=query)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        groups = request.user.groups.all().values_list('name', flat=True) # obtenemos los grupos del usuario para ver si tiene permisos para acceder a la tarea
        task = get_object_or_404(Task, pk=task_id) # obtenemos la tarea para recuperar el usuario asignado
        history = ChangeLog.objects.filter(task_id=task_id).order_by('-dateofchange') # Obtener el historial filtrado por task_id

        if history:
            user_ids = [h.user_id for h in history]
            users = User.objects.filter(pk__in=user_ids)
            # Combinar historiales con usuarios
            history = [(h, u) for h in history for u in users if u.pk == h.user_id]

        # si el usuario es el asignado a la tarea o el usuario tiene rol de admin o manager...
        if task.employee_user == request.user or 'admin' in groups or 'manager' in groups:
            return render(request, 'tasks/task_detail.html', {
                'task': task,
                'history': history
            })
        else:
            return redirect('index') # si alguien intenta entrar sin permisos, se le redirige a index
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
                return render(request, 'tasks/task_detail.html', {
                    'task': task,
                    'form': form,
                    'error': "Error actualizando task"
                })


#endregion

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def tasks_client_pending(request):
    # fecha de compeltada, y manager rellena, cliente vacía
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=False, datecompleted_client_approval__isnull=True)

    return render(request, 'tasks/tasks_client_pending.html', {
        'tasks': tasks
    })

@login_required
@allowed_user(allowed_roles=['admin', 'manager', 'customer'])
def tasks_completed(request):
    # filtramos las tareas por usuario
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    #tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })

@login_required
def task_update(request, task_id):   
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
        form = EmployeeTaskForm(instance=task)
        return render(request, 'tasks/task_delivery.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
            form = EmployeeTaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
                return render(request, 'tasks/task.html', {
                    'task': task,
                    'form': form,
                    'error': "Error actualizando task"
                })

@login_required
def task_delivery(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
        form = EmployeeTaskForm(instance=task)
        return render(request, 'tasks/task_delivery.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
            form = EmployeeTaskForm(request.POST, request.FILES, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
                return render(request, 'tasks/task_delivery.html', {
                    'task': task,
                    'form': form,
                    'error': "Error actualizando task"
                })
        
@login_required    
def complete_task(request, task_id):
    # meter try
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
        form = EmployeeTaskForm(request.POST, instance=task)
        task.save()

        # Validation - para entregar, los checks deben estar marcados todos
        if all([task.windows, task.chassis, task.wheels, task.upholstery]):
            task.datecompleted = timezone.now()
            task.flag_rechazado = False
            task.save()

            # Create changelog entry
            ChangeLog.objects.create(
                task_id=task_id,
                dateofchange = timezone.now(),
                user_id=request.user.id,
                descripcion_estado = "Tarea completada",
                changereason="Tarea completada",
                comment="Entrada automática",
        
            )

            return redirect('tasks')
        
        return render(request, 'tasks/task_delivery.html', {
            'task': task,
            'form': form,
            'error': "Error - Antes de entregar debe completar todas las tareas"
            })

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def tasks_history(request):
    tasks = Task.objects.all() # todas las tareas
    return render(request, 'tasks/tasks_history.html', {
        'tasks': tasks
    })

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def task_history_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    # Obtener el historial filtrado por task_id
    history = ChangeLog.objects.filter(task_id=task_id).order_by('-dateofchange') # Obtener el historial filtrado por task_id

    if history:
        user_ids = [h.user_id for h in history]
        users = User.objects.filter(pk__in=user_ids)
        # Combinar historiales con usuarios
        history = [(h, u) for h in history for u in users if u.pk == h.user_id]


    if request.method == 'GET':
        return render(request, 'tasks/task_history_detail.html', {
            'task': task,
            'history': history
        })
    else:
        return redirect('index')

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def task_manager_pending(request):
    # Mostrar todas las tareas entregadas por employee, independientemente del usuario
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=True).order_by('-datecompleted')
    return render(request, 'tasks/task_manager_pending.html', {
        'tasks': tasks
    })

@login_required
def task_manager_approval(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        try:

            form = TaskDeliveryClientForm(request.POST)
            if form.is_valid():
                task.datecompleted_manager_approval = timezone.now()
                task.save()

                # Create changelog entry
                ChangeLog.objects.create(
                    task_id=task_id,
                    dateofchange = timezone.now(),
                    user_id=request.user.id,
                    descripcion_estado = "Tarea Aprobada por manager",
                    changereason= "Tarea Aprobada por manager",
                    comment="Entrada automática",
            
                )                
                
            return redirect('task_manager_pending')
        except ValueError:
                return redirect('task_manager_pending')


#region manager

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def task_manager_denial(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'GET':
        print('task_manager_denial - get')
        return render(request, 'tasks/task_manager_denial.html', {
            'task': task,
            'form': TaskFormRechazoManager
        })
    else:
        print('task_manager_denial - post')
        try:
            form = TaskFormRechazoManager(request.POST)
            if form.is_valid():
                task.datecompleted = None
                task.datecompleted_manager_approval = None
                task.datecompleted_client_approval = None
                task.motivo_rechazo_manager = form.cleaned_data['motivo_rechazo_manager']
                task.comentario_rechazo_manager = form.cleaned_data['comentario_rechazo_manager']
                task.flag_rechazado = True
                task.save()

                # Create changelog entry
                ChangeLog.objects.create(
                    task_id=task_id,
                    dateofchange = timezone.now(),
                    user_id=request.user.id,
                    descripcion_estado = "Tarea Rechazada por manager",
                    changereason= MotivoRechazo.objects.get(codigo=task.motivo_rechazo_manager).descripcion,
                    comment=task.comentario_rechazo_manager,
            
                )

            return redirect('task_manager_pending')
        except ValueError:
            return redirect('task_manager_pending')

#endregion



#region cliente

@login_required
@allowed_user(allowed_roles=['customer'])
def task_client_pending(request):
    # Mostrar todas las tareas entregadas por employee, independientemente del usuario
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=False, datecompleted_client_approval__isnull=True).order_by('-datecompleted')
    return render(request, 'tasks/task_client_pending.html', {
        'tasks': tasks
    })

@login_required
@allowed_user(allowed_roles=['customer'])
def task_client_approval(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        try:

            form = TaskDeliveryClientForm(request.POST)
            if form.is_valid():
                task.datecompleted_client_approval = timezone.now()
                task.save()

                # Create changelog entry
                ChangeLog.objects.create(
                    task_id=task_id,
                    dateofchange = timezone.now(),
                    user_id=request.user.id,
                    descripcion_estado = "Tarea Aprobada por cliente",
                    changereason= "Tarea Aprobada por cliente",
                    comment="Entrada automática",
            
                )                
                
            return redirect('task_client_pending')
        except ValueError:
                return redirect('task_client_pending')


@login_required
@allowed_user(allowed_roles=['customer'])
def task_client_denial(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'GET':
        return render(request, 'tasks/task_client_denial.html', {
            'task': task,
            'form': TaskFormRechazoCliente
        })
    else:
        try:
            form = TaskFormRechazoCliente(request.POST)
            if form.is_valid():
                task.datecompleted = None
                task.datecompleted_manager_approval = None
                task.datecompleted_client_approval = None
                task.motivo_rechazo_cliente = form.cleaned_data['motivo_rechazo_cliente']
                task.comentario_rechazo_cliente = form.cleaned_data['comentario_rechazo_cliente']
                task.flag_rechazado = True
                task.save()

                # Create changelog entry
                ChangeLog.objects.create(
                    task_id=task_id,
                    dateofchange = timezone.now(),
                    user_id=request.user.id,
                    descripcion_estado = "Tarea Rechazada por cliente",
                    changereason= MotivoRechazo.objects.get(codigo=task.motivo_rechazo_cliente).descripcion,
                    comment=task.comentario_rechazo_cliente,
                )

            return redirect('task_client_pending')
        except ValueError:
            return redirect('task_client_pending')

#endregion




    


#region admin/manager

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def create_task(request):
    if request.method == 'GET':
        return render(request, 'tasks/create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            project = get_object_or_404(Project, id=1)
            new_task.project = project
            new_task.save()

            # Now you have access to the newly created task's ID
            task_id = new_task.id  # Access the ID attribute

            # Create changelog entry
            ChangeLog.objects.create(
                task_id=task_id,
                dateofchange = timezone.now(),
                user_id=request.user.id,
                descripcion_estado = "Alta en el sistema",
                changereason="Alta en el sistema",  # Entrada (1) --> Entrada --> (21)
                comment=None,  # Adjust comment as needed
        
            )
            
            return render(request, 'index.html', {
                'form': TaskForm
            })
        except ValueError:
            return render(request, 'tasks/create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid data'
            })

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

#endregion








#region utilities

def dashboard(request):
    # Obtener todas las altas en el sistema agrupadas por año y mes
    altas_por_mes = ChangeLog.objects.filter(changereason='Alta en el sistema') \
        .extra(select={'year_month': "strftime('%%Y-%%m', dateofchange)"}) \
        .values('year_month') \
        .annotate(num_altas=Count('id'))

    fig = px.bar(
        x = [alta['year_month'] for alta in altas_por_mes],
        y = [alta['num_altas'] for alta in altas_por_mes]
    )

    chart = fig.to_html()



    # obtener todos los rechazos por mes
    rechazos_por_mes = ChangeLog.objects.filter(descripcion_estado__icontains='Rechazo') \
        .extra(select={'year_month': "strftime('%%Y-%%m', dateofchange)"}) \
        .values('year_month') \
        .annotate(num_altas=Count('id'))

    fig = px.bar(
        x = [rechazo['year_month'] for rechazo in rechazos_por_mes],
        y = [rechazo['num_altas'] for rechazo in rechazos_por_mes]
    )

    chart_rechazos_por_mes = fig.to_html()



    # Consulta para obtener los motivos de rechazo
    
    # Ejemplo de consulta SQL
    sql_query = """
        SELECT t.changereason, COUNT(t.task_id) AS cuenta_rechazos
        FROM (
            SELECT task_id, descripcion_estado, changereason 
            FROM myapp_changelog
            WHERE descripcion_estado LIKE '%Rechazo%'
        ) AS t
        GROUP BY t.changereason
    """

    # Ejecutar la consulta SQL
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        resultados = cursor.fetchall()

    # Crear el gráfico de barras
    fig = px.bar(
        x=[resultado[0] for resultado in resultados],  # changereason
        y=[resultado[1] for resultado in resultados],  # cuenta_rechazos
        labels={'x': 'Motivo de Rechazo', 'y': 'Cantidad de Rechazos'}
    )

    chart_rechazos_por_empleado = fig.to_html()





    return render(request, 'dashboard/dashboard.html', {
        'chart': chart,
        'chart_rechazos_por_mes': chart_rechazos_por_mes,
        'chart_rechazos_por_empleado': chart_rechazos_por_empleado
    })

def calcular_porcentaje_vehiculos_rechazados():
    # Contar el total de vehículos en la tabla ChangeLog
    total_vehiculos = ChangeLog.objects.filter(changereason='Alta en el sistema').values('task_id').distinct().count()

    # Contar los registros donde la descripción del estado indica que la tarea fue rechazada por el manager o el cliente
    registros_rechazados = ChangeLog.objects.filter(
        Q(descripcion_estado__icontains='Tarea Rechazada por manager') |
        Q(descripcion_estado__icontains='Tarea Rechazada por cliente')
    ).count()

    # Calcular el porcentaje de vehículos rechazados
    if total_vehiculos > 0:
        porcentaje_rechazados = (registros_rechazados / total_vehiculos) * 100
    else:
        porcentaje_rechazados = 0

    return porcentaje_rechazados


#endregion