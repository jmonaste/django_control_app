from django import forms
from django.forms import ModelForm
from .models import Task, PostImage

class createNewTask(forms.Form):
    vin = forms.CharField(label='Titulo de tarea', max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
    description = forms.CharField(label="Descipcion de la tarea", widget=forms.Textarea(attrs={'class': 'input'})) 


class createNewProject(forms.Form):
    name = forms.CharField(label="Nombre del proyecto", max_length=200, widget=forms.Textarea(attrs={'class': 'input'}))

# segundo curso - añadido
class EmployeeTaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['windows', 'chassis', 'wheels', 'upholstery']
        labels = {
            'windows': 'Ventanas',
            'chassis': 'Carrocería', 
            'wheels': 'Llantas', 
            'upholstery': 'Tapicería'
        }
        

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['vin' , 'project', 'client', 'carbrand', 'carmodel', 'comment', 'deadline',
                'datecompleted', 'employee_user', 'responsible_user', 'priority', 'description', 'important',
                'windows', 'chassis', 'wheels', 'upholstery']
        

class TaskDeliveryClientForm(forms.ModelForm):
  task_id = forms.IntegerField(widget=forms.HiddenInput())
  class Meta:
    model = Task
    fields = ['task_id']

class TaskClientApprovalForm(forms.ModelForm):
  task_id = forms.IntegerField(widget=forms.HiddenInput())
  class Meta:
    model = Task
    fields = ['task_id']

class TaskUploadImage(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['carimage']


class TaskFormRechazoManager(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['motivo_rechazo_manager', 'comentario_rechazo_manager']

class TaskFormRechazoCliente(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['motivo_rechazo_cliente', 'comentario_rechazo_cliente']

# Formulario para usar el modelo de imagen del post
class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['images']


class UploadFileForm(forms.Form):
    file = forms.FileField()
