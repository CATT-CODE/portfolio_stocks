# Generated by Django 4.0.4 on 2022-05-20 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocksapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
