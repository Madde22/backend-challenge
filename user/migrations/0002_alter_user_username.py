# Generated by Django 4.2.4 on 2023-08-20 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default=None, max_length=255, unique=True, verbose_name='username'),
            preserve_default=False,
        ),
    ]
