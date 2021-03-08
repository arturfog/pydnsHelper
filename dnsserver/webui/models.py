from django.db import models

# Create your models here.
class Host(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    comment = models.CharField(max_length=250, help_text='Comment', null=True)
    created = models.DateTimeField(null=True,auto_now_add=True, blank=True)
    hits = models.IntegerField(help_text='Hits', null=False, default=0)
    blocked = models.BooleanField(null=False, default=False)
    indexes = [
        models.Index(fields=['url',]),
    ]

    def __str__(self):
        """String for representing the Model object."""
        return self.url

class IPv4(models.Model):
    id = models.AutoField(primary_key=True)
    host =  models.ForeignKey('Host', on_delete=models.CASCADE)
    ip = models.CharField(max_length=16, help_text='IPv4', null=False, default="0.0.0.0")
    ttl = models.IntegerField(help_text='TTL', null=False, default=-1)

class IPv6(models.Model):
    id = models.AutoField(primary_key=True)
    host =  models.ForeignKey('Host', on_delete=models.CASCADE)
    ip = models.CharField(max_length=16, help_text='IPv4', null=False, default="0.0.0.0")
    ttl = models.IntegerField(help_text='TTL', null=False, default=-1)
    

class HostSources(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200, help_text='URL', null=False, unique=True)
    last_updated = models.DateTimeField(null=True,auto_now_add=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.url

class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    msg = models.TextField(max_length=512, help_text='msg', null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return "Log: %s %s" % (self.msg, self.timestamp)

class ClientIP(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.TextField(max_length=15, help_text='ip', null=False, unique=True)
    
    def __str__(self):
        """String for representing the Model object."""
        return self.ip

class StatsHosts(models.Model):
    id = models.AutoField(primary_key=True)
    host = models.TextField(max_length=122, help_text='host', null=False)

class BlockedClients(models.Model):
    id = models.AutoField(primary_key=True)
    clientIP = models.ForeignKey('ClientIP', on_delete=models.CASCADE)

class Stats(models.Model):
    id = models.AutoField(primary_key=True)
    host = models.ForeignKey('StatsHosts', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)
    client = models.ForeignKey('ClientIP', on_delete=models.CASCADE)