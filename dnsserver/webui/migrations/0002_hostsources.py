# Generated by Django 2.1.3 on 2018-11-11 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostSources',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(help_text='URL', max_length=200, unique=True)),
            ],
        ),
    ]
