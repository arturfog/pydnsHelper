from django.db import models

# Create your models here.


class Host(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    ipv4 = models.CharField(max_length=16, help_text='IPv4', null=False, default="0.0.0.0")
    ipv6 = models.CharField(max_length=40, help_text='IPv6', null=False, default="::0")
    ttl = models.IntegerField(help_text='TTL', null=False, default=999)
    hits = models.IntegerField(help_text='Hits', null=False, default=0)
    created = models.DateTimeField(null=True)
    comment = models.CharField(max_length=250, help_text='Comment', null=True)

    indexes = [
        models.Index(fields=['url',]),
    ]

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
    date = models.DateField(null=False)

class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    msg = models.TextField(max_length=512, help_text='msg', null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return "Log: %s %s" % (self.msg, self.timestamp)