# Generated by Django 5.0.4 on 2024-05-05 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_delete_car_task_motivo_devolucion'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='comment_client',
            field=models.TextField(blank=True),
        ),
    ]