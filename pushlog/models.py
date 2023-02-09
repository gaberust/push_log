from django.db import models

# Create your models here.


class Device(models.Model):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=256)

    def __str__(self):
        return f'Device {self.id}: {self.name}'


class Report(models.Model):
    message = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'[{self.device.name} - {self.reported_at}]: {self.message}'
