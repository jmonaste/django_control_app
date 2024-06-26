# Generated by Django 5.0.4 on 2024-04-29 20:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_carbrand_carmodel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carmodel',
            old_name='name',
            new_name='model',
        ),
        migrations.AddField(
            model_name='carmodel',
            name='brand',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.carbrand'),
            preserve_default=False,
        ),
    ]
