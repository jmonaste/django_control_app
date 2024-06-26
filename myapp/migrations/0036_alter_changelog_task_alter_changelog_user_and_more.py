# Generated by Django 5.0.4 on 2024-05-25 04:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0035_post'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelog',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.task'),
        ),
        migrations.AlterField(
            model_name='changelog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='carbrand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.carbrand'),
        ),
        migrations.AlterField(
            model_name='task',
            name='carmodel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.carmodel'),
        ),
        migrations.AlterField(
            model_name='task',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.client'),
        ),
    ]
