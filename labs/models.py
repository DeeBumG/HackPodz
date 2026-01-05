from django.db import models

class PodInstance(models.Model):
    name = models.CharField(max_length=100)  # actual pod name in Kubernetes
    box_type = models.CharField(
        max_length=20,
        choices=[
            ('kali', 'Kali'),
            ('ftp', 'FTP'),
            ('mysql', 'MySQL'),
        ]
    )
    ssh_password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
