# Generated by Django 5.0.4 on 2024-05-07 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0032_changelog_descripcion_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelog',
            name='changereason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='changelog',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]