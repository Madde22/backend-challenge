# Generated by Django 4.2.4 on 2023-08-20 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('sys_id', models.AutoField(primary_key=True, serialize=False)),
                ('session_key', models.CharField(blank=True, max_length=1024)),
                ('path', models.CharField(blank=True, max_length=1024)),
                ('method', models.CharField(blank=True, max_length=8)),
                ('data', models.TextField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=45)),
                ('referrer', models.CharField(blank=True, max_length=512, null=True)),
                ('timestamp', models.DateTimeField(blank=True)),
            ],
            options={
                'verbose_name': 'Access Logs',
                'verbose_name_plural': 'Access Log',
                'db_table': 'access_logs',
                'ordering': ['pk'],
            },
        ),
    ]