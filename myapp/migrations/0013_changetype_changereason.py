# Generated by Django 5.0.4 on 2024-04-29 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_rename_name_carbrand_brandname_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changetype', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ChangeReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changereason', models.CharField(max_length=100)),
                ('changetype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.changetype')),
            ],
        ),
    ]