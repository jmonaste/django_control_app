# Generated by Django 5.0.4 on 2024-05-03 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_task_carimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='carimage',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
