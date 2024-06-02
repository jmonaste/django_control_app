from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ..models import MotivoRechazo, Task




def get_motivos_rechazo(request):
    motivos=list(MotivoRechazo.objects.values())

    if (len(motivos)>0):
        data={'message':"Success", 'motivos':motivos}
    else:
        data={'message':"Not found"}

    return JsonResponse(data)


def get_task(request, task_id):
    task = list(Task.objects.filter(id=task_id).values())

    if (len(task)>0):
        data={'message':"Success", 'tarea':task}
    else:
        data={'message':"Not found"}

    return JsonResponse(data)

