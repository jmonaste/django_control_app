from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ..models import Project, Task, ChangeLog, ChangeReason, MotivoRechazo, PostImage, Post
from django.shortcuts import get_object_or_404, render, redirect
from ..forms import createNewTask, createNewProject
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from ..forms import TaskForm, EmployeeTaskForm, TaskDeliveryClientForm, TaskUploadImage, TaskClientApprovalForm, TaskFormRechazoCliente, TaskFormRechazoManager, TaskFormRechazoCliente, PostImageForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ..decorators import unauthenticated_user, allowed_user
from django.db.models import Q  # Import the Q object
from django.db.models import Count, Prefetch
import plotly.express as px
from django.db import connection




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
        history = ChangeLog.objects.filter(task_id=task_id).order_by('-dateofchange') # Obtener el historial filtrado por task_id

        if history:
            user_ids = [h.user_id for h in history]
            users = User.objects.filter(pk__in=user_ids)
            # Combinar historiales con usuarios
            history = [(h, u) for h in history for u in users if u.pk == h.user_id]

        task = get_object_or_404(Task, pk=task_id)
        form = EmployeeTaskForm(instance=task)
        imageForm = TaskUploadImage(instance=task)
        return render(request, 'tasks/task_detail.html', {
            'task': task,
            'form': form,
            'history': history,
            'imageForm': imageForm
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
    history = ChangeLog.objects.filter(task_id=task_id).order_by('-dateofchange') # Obtener el historial filtrado por task_id

    if history:
        user_ids = [h.user_id for h in history]
        users = User.objects.filter(pk__in=user_ids)
        # Combinar historiales con usuarios
        history = [(h, u) for h in history for u in users if u.pk == h.user_id]

    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
        images = PostImage.objects.filter(task=task)
        form = EmployeeTaskForm(instance=task)
        imageForm = TaskUploadImage(instance=task)

        return render(request, 'tasks/task_delivery.html', {
            'task': task,
            'form': form,
            'history': history,
            'imageForm': imageForm,
            'images': images
        })


    else:
        try:

            task = get_object_or_404(Task, pk=task_id, employee_user=request.user)
            field = request.POST.get('field')
            value = request.POST.get('value') == 'true'
            
            if hasattr(task, field):
                setattr(task, field, value)
                task.save()
                return redirect('tasks')
            else:
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



def upload_image(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(pk=task_id)
        images = request.FILES.getlist('images')  # Nombre del campo en el formulario
        
        if not images:
            return JsonResponse({'status': 'error', 'message': 'No images uploaded'})

        errors = []
        for image in images:
            image_form = PostImageForm({'task': task.id}, {'images': image})
            if image_form.is_valid():
                post_image = image_form.save(commit=False)
                post_image.task = task
                post_image.save()
            else:
                errors.append(image_form.errors)
        
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors})
        
        return JsonResponse({'status': 'success', 'message': 'Images uploaded successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})