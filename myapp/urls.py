from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings  # new
from django.urls import path, include  # new
from django.conf.urls.static import static  # new
from .views import global_views, client_tasks_views, manager_tasks_views, worker_tasks_views, models_views

urlpatterns = [    
    path('', global_views.index, name="index"),
    path('about/', global_views.about, name="about"),
    path('signin/', global_views.signin, name="signin"),
    path('signup/', global_views.signup, name="signup"),
    path('logout/', global_views.signout, name="logout"),
    path('projects/', global_views.projects, name="projects"),
    path('create_project/', global_views.create_project, name="create_project"),
    path('projects/<int:id>', global_views.project_detail, name="project_detail"),

    path('tasks/', worker_tasks_views.tasks, name="tasks"),
    path('tasks/task_search', worker_tasks_views.task_search, name="task_search"),
    
    path('tasks_completed/', global_views.tasks_completed, name="tasks_completed"),
    path('task_detail/<int:task_id>', worker_tasks_views.task_detail, name="task_detail"),
    
    path('task_delivery/<int:task_id>', worker_tasks_views.task_delivery, name="task_delivery"),
    


    path('task_manager_pending/', manager_tasks_views.task_manager_pending, name="task_manager_pending"),
    path('task_manager_approval/<int:task_id>', manager_tasks_views.task_manager_approval, name="task_manager_approval"), 
    path('task_manager_denial/<int:task_id>/', manager_tasks_views.task_manager_denial, name="task_manager_denial"),  

    path('upload/', manager_tasks_views.upload_file, name='upload_file'),



    path('task_client_pending/', client_tasks_views.task_client_pending, name="task_client_pending"),
    path('task_client_approval/<int:task_id>/', client_tasks_views.task_client_approval, name="task_client_approval"),    
    path('task_client_denial/<int:task_id>/', client_tasks_views.task_client_denial, name="task_client_denial"),    

    
    
    path('approval_pending_tasks/<int:task_id>/<str:action>', global_views.task_client_pending, name="task_client_pending"),


    path('dashboard/', global_views.dashboard, name="dashboard"),
    
    path('tasks/<int:task_id>/complete', global_views.complete_task, name="complete_task"),
    path('tasks/<int:task_id>/delete', global_views.delete_task, name="delete_task"),
    
    path('create_task/', global_views.create_task, name="create_task"),
    path('tasks_history/', global_views.tasks_history, name="tasks_history"),
    path('task_history_detail/<int:task_id>', global_views.task_history_detail, name="task_history_detail"),


    path('tasks_client_pending/', global_views.tasks_client_pending, name="tasks_client_pending"),

    path('motivos_rechazo/', models_views.get_motivos_rechazo, name="get_motivos_rechazo"),
    path('tarea/<int:task_id>', models_views.get_task, name="get_task"),
    path('upload_image/<int:task_id>/', worker_tasks_views.upload_image, name='upload_image'),
]  


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #new