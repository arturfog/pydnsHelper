# Generated by Django 2.1.5 on 2019-01-27 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0005_auto_20190127_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='comment',
            field=models.CharField(help_text='Comment', max_length=250, null=True),
        ),
    ]
