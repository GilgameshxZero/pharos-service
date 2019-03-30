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
    facebook_id = models.CharField(
        max_length=128, primary_key=True, unique=True)
    pdf_url = models.TextField()
    kerberos = models.CharField(max_length=32, unique=True)
    sided = models.CharField(max_length=1, choices=JOB_SIDED)
    printer_type = models.CharField(max_length=1, choices=PRINTER_TYPE)
    n_copies = models.IntegerField(default=0)


USER_STATE = (
    ('P', 'PDF'),
    ('K', 'KERBEROS'),
    ('S', 'SIDED'),
    ('T', 'PRINTER_TYPE'),
    ('N', 'N_COPIES')
)
NEXT_STATE_RESPONSE = {
    'P': 'What\'s your kerberos?',
    'K': 'Do you want to print \'single\' or \'double\' sided?',
    'S': 'Do you want to print \'bw\' or color\'?',
    'T': 'How many copies do you want to print? Type a number.',
    'N': 'We\'ve sent your order to the printer!'
}


class PrintUserState(models.Model):
    facebook_id = models.CharField(
        max_length=128, primary_key=True, unique=True)
    state = models.CharField(max_length=1, choices=USER_STATE)
