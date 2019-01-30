from django.db import models

# Create your models here.


class Host(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    ip = models.CharField(max_length=64, help_text='IP', null=False)
    ttl = models.IntegerField(help_text='TTL', null=False)
    hits = models.IntegerField(help_text='Hits', null=False, default=0)
    last_access = models.DateTimeField(null=True)
    comment = models.CharField(max_length=250, help_text='Comment', null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.url

class HostSources(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    last_updated = models.DateTimeField(null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.url

class Traffic(models.Model):
    id = models.AutoField(primary_key=True)
    hits = models.IntegerField(help_text='Hits', null=False, default=0)
    date = models.DateTimeField(null=True)

class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    msg = models.TextField(max_length=512, help_text='msg', null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)