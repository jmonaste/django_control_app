from django.urls import path
from . import views

urlpatterns = [    
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('car_detail/', views.car_detail, name="car_detail"),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.signout, name="logout"),
    path('projects/', views.projects, name="projects"),
    path('projects/<int:id>', views.project_detail, name="project_detail"),
    path('cars/', views.cars, name="cars"),
    path('tasks/', views.tasks, name="tasks"),
    path('tasks_completed/', views.tasks_completed, name="tasks_completed"),
    path('task_detail/<int:task_id>', views.task_detail, name="task_detail"),
    path('tasks/<int:task_id>/complete', views.complete_task, name="complete_task"),
    path('tasks/<int:task_id>/delete', views.delete_task, name="delete_task"),
    path('tasks/task_search', views.task_search, name="task_search"),
    path('create_task/', views.create_task, name="create_task"),
    path('create_project/', views.create_project, name="create_project"),
    path('signin/', views.signin, name="signin")
]  