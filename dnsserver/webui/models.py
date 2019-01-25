from django.db import models

# Create your models here.


class Host(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    ip = models.CharField(max_length=64, help_text='IP', null=False)
    ttl = models.IntegerField(help_text='TTL', null=False)
    hits = models.IntegerField(help_text='Hits', null=True)
    last_access = models.DateTimeField(null=True)
    comment = models.CharField(max_length=250, help_text='Comment')

    def __str__(self):
        """String for representing the Model object."""
        return self.url


class HostSources(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.url

