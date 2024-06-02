from django.shortcuts import render
from ..models import Task, ChangeLog, MotivoRechazo
from django.shortcuts import get_object_or_404, render, redirect
from ..forms import TaskDeliveryClientForm, TaskFormRechazoCliente, TaskFormRechazoManager, TaskFormRechazoCliente
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ..decorators import allowed_user



# Create your views here.

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


