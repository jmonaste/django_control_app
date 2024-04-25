from django import forms
from django.forms import ModelForm
from .models import Task

class createNewTask(forms.Form):
    title = forms.CharField(label='Titulo de tarea', max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
    description = forms.CharField(label="Descipcion de la tarea", widget=forms.Textarea(attrs={'class': 'input'})) 


class createNewProject(forms.Form):
    name = forms.CharField(label="Nombre del proyecto", max_length=200, widget=forms.Textarea(attrs={'class': 'input'}))

# segundo curso - añadido
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title' , 'description', 'important']