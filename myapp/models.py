from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Car(models.Model):
    pin = models.IntegerField()
    marca = models.CharField(max_length=30)
    modelo = models.CharField(max_length=30)
    fecha_alta_sistema = models.DateField()
    done_carroceria = models.BooleanField(default=False)
    done_vidrios = models.BooleanField(default=False)
    done_llantas = models.BooleanField(default=False)
    done_interior = models.BooleanField(default=False)
    fecha_entrega = models.DateField()

    def __str__(self):
        return self.pin


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' - ' + self.project.name + ' - ' + self.description
