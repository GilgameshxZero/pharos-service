from __future__ import unicode_literals

from django.db import models

# Create your models here.
JOB_SIDED = (
	('S', 'SINGLE'),
	('D', 'DOUBLE')
)
PRINTER_TYPE = (
	('B', 'BLACKWHITE'),
	('C', 'COLOR')
)
class PrintJob(models.Model):
	facebook_id = models.CharField(max_length=128, primary_key=True, unique=True)
	pdf_url = models.TextField()
	kerberos = models.CharField(max_length=32, unique=True)
	sided = models.CharField(max_length=1, choices=JOB_SIDED)
	printer_type = models.CharField(max_length=1, choices=PRINTER_TYPE)
	n_copies = models.IntegerField(default=0)