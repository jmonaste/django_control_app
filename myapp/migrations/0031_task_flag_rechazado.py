# Generated by Django 5.0.4 on 2024-05-07 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0030_alter_task_motivo_rechazo_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='flag_rechazado',
            field=models.BooleanField(default=False),
        ),
    ]