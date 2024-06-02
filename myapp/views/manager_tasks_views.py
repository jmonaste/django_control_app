from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ..models import Project, Task, ChangeLog, ChangeReason, MotivoRechazo, Client, CarBrand, CarModel
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from ..forms import createNewTask, createNewProject
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from ..forms import TaskForm, EmployeeTaskForm, TaskDeliveryClientForm, TaskUploadImage, TaskClientApprovalForm, TaskFormRechazoCliente, TaskFormRechazoManager, TaskFormRechazoCliente
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ..decorators import unauthenticated_user, allowed_user
from django.db.models import Q  # Import the Q object
from django.db.models import Count, Prefetch
import plotly.express as px
from django.db import connection
import pandas as pd
from django.contrib import messages
from datetime import datetime
from ..forms import UploadFileForm
from ..models import Task
from django.core.exceptions import ObjectDoesNotExist
from ..resources import TaskResource
from tablib import Dataset


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






def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        try:
            # Leer el archivo Excel usando pandas
            df = pd.read_excel(file)

            # Convertir las columnas de fecha a cadenas
            if 'deadline' in df.columns:
                df['deadline'] = df['deadline'].astype(str)

            # Procesar cada fila por separado
            results = []
            for index, row in df.iterrows():
                try:
                    vin = row['vin']
                    project_name = row['proyecto']
                    client_name = row['cliente']
                    carbrand = row['carbrand']
                    carmodel = row['carmodel']
                    comment = row['comment'] if pd.notnull(row['comment']) else None
                    created = datetime.now()  # Fecha y hora actual
                    deadline = row['deadline'] if pd.notnull(row['deadline']) else None
                    employee_user = row['employee']
                    responsible_user = row['responsible']
                    priority = row['priority']
                    description = row['description'] if pd.notnull(row['description']) else None
                    important = row['important']
                    deniedbyclient = False
                    windows = False
                    chassis = False
                    wheels = False
                    upholstery = False
                    flag_rechazado = False

                    # Validar el campo VIN
                    if Task.objects.filter(vin=vin).exists():
                        raise IntegrityError(f'El VIN "{vin}" ya existe en la base de datos.')
                    
                    # Validar el campo proyecto
                    try:
                        project = Project.objects.get(name=project_name)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El proyecto "{project_name}" no existe en la base de datos.')
                    
                    # Validar el campo cliente
                    try:
                        client = Client.objects.get(name=client_name)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El cliente "{client_name}" no existe en la base de datos.')

                    # Validar el campo carbrand
                    try:
                        car_brand = CarBrand.objects.get(brandname=carbrand)
                    except ObjectDoesNotExist:
                        raise ValueError(f'La marca de coches "{car_brand}" no existe en el sistema.')

                    # Validar el campo carmodel
                    try:
                        car_model = CarModel.objects.get(model=carmodel)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El modelo "{car_model}" no existe en el sistema.')
                    
                    # Validar que la reacion entre marca y modelo 
                    try:
                        car_model = CarModel.objects.get(model=carmodel)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El modelo "{car_model}" no existe en el sistema.')
                    


                    # Validar campos de usuario
                    try:
                        responsible_user_info = User.objects.get(username=responsible_user)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El usuario "{responsible_user}" no existe en el sistema.')

                    try:
                        employee_user_info = User.objects.get(username=employee_user)
                    except ObjectDoesNotExist:
                        raise ValueError(f'El usuario "{employee_user}" no existe en el sistema.')




                    # Validar del campo prioridad
                    if priority != 1 and priority != 0:
                        raise ValueError(f'El valor del campo "prioridad" en la fila {index + 2} no es válido. Sólo se permiten los valores 0 y 1.')
                    


                    # Consulta SQL para insertar los datos
                    sql_query = """
                        INSERT INTO myapp_task (
                            vin, project_id, client_id, carbrand_id, carmodel_id, comment, created,
                            deadline, employee_user_id, responsible_user_id, priority, description, important, deniedbyclient, windows, chassis, wheels, upholstery, flag_rechazado
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    with connection.cursor() as cursor:
                        cursor.execute(sql_query, [
                            vin, project.id, client.id, car_brand.id, car_model.id, comment, created,
                            deadline, employee_user_info.id, responsible_user_info.id, priority, description, important, deniedbyclient, windows, chassis, wheels, upholstery, flag_rechazado
                        ])
                        cursor.execute("SELECT last_insert_rowid()")
                        new_id = cursor.fetchone()[0]


                    # Create changelog entry
                    ChangeLog.objects.create(
                        task_id=new_id,
                        dateofchange = created,
                        user_id=request.user.id,
                        descripcion_estado = "Alta en el sistema",  
                        changereason="Alta en el sistema",
                        comment="Alta en el sistema desde carga de fichero"
                        )




                    results.append({'index': index, 'status': 'success', 'message': f'{index + 2} - {vin} VIN insertado correctamente en el sistema.'})
                except Exception as e:
                    results.append({'index': index, 'status': 'error', 'message': f'Error en fila {index + 2}: {e}'})
            
            return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        form = UploadFileForm()
        return render(request, 'tasks/tasks_upload.html', {'form': form})


