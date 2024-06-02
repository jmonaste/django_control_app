from import_export import resources
from .models import Task

class TaskResource(resources.ModelResource):
    class Meta:
        model = Task
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('vin',)  # Usamos 'vin' como identificador único
        fields = ('vin', 'project', 'client', 'carbrand', 'carmodel', 'comment', 'deadline', 'priority', 'description', 'important')
