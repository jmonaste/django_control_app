# Generated by Django 5.0.4 on 2024-05-07 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0031_task_flag_rechazado'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelog',
            name='descripcion_estado',
            field=models.TextField(blank=True, null=True),
        ),
    ]
