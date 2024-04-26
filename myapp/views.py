from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Project, Task, Car
from django.shortcuts import get_object_or_404, render, redirect
from .forms import createNewTask, createNewProject
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    title = "Control de operaciones"
    return render(request, 'index.html', {
        'title': title
    })


def helloworld(request):
    return render(request, 'signup.html', {
        'form': UserCreationForm
    })


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


def about(request):
    username = 'jmonaste'
    return render(request, 'about.html', {
        'username': username
    })


def projects(request):
    # projects = list(Project.objects.values())
    projects = Project.objects.all()
    # return JsonResponse(projects, safe=False)
    return render(request, 'projects/projects.html', {
        'projects': projects
    })


def cars(request):
    cars = Car.objects.all()
    return render(request, 'cars/cars.html', {
        'cars': cars
    })

@login_required
def tasks(request):
    # filtramos las tareas por usuario
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    #tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
def task_search(request):
    # filtramos las tareas por usuario, por pendiente y por id (patente)
    query = request.GET.get('q')
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True, title__icontains=query)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
def tasks_completed(request):
    # filtramos las tareas por usuario
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    #tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


# def create_task(request):
#    if request.method == 'GET':
#        return render(request, 'tasks/create_task.html', {
#            'form': createNewTask()})
#    else:
#        Task.objects.create(title=request.POST['title'],
#                            description=request.POST['description'], project_id=2)
#        return redirect('tasks')

@login_required
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
            print(new_task)
            return render(request, 'index.html', {
                'form': TaskForm
            })
        except ValueError:
            return render(request, 'tasks/create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid data'
            })




@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # task = Task.objects.get(pk=task_id)
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'tasks/task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
                return render(request, 'tasks/task_detail.html', {
                    'task': task,
                    'form': form,
                    'error': "Error actualizando task"
                })


@login_required    
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')








@login_required
def create_project(request):
    if request.method == 'GET':
        return render(request, 'projects/create_project.html', {
            'form': createNewProject()
        })
    else:
        project = Project.objects.create(name=request.POST["name"])
        return redirect('projects')

@login_required
def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    tasks = Task.objects.filter(project_id=id)
    print(project)
    return render(request, 'projects/detail.html', {
        'project': project,
        'tasks': tasks
    })

@login_required
def car_detail(request):
    username = 'jmonaste'
    return render(request, 'cars/car_detail.html', {
        'username': username
    })


def signout(request):
    logout(request)
    return redirect('index')


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

# 1:01:31
