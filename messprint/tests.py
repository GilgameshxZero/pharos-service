from django.test import TestCase
from messprint.models import PrintJob, JOB_SIDED, PRINTER_TYPE

# Create your tests here.
class PrintJobTests(TestCase):
	def setUp(self):
		PrintJob.objects.create(
			facebook_id='some_test_id',
			pdf_url='http://some_url.pdf',
		)

	def test_fetch_print_job(self):
		print_job = PrintJob.objects.get(facebook_id='some_test_id')
		self.assertTrue(print_job, 'The print job doesn\'t exist')

	def test_set_kerberos(self):
		print_job = PrintJob.objects.get(facebook_id='some_test_id')
		print_job.kerberos = 'some_kerberos'
		print_job.save()
		self.assertTrue(print_job.kerberos == 'some_kerberos', 'The kerberos doesn\'t match')

	def test_set_sided(self):
		print_job = PrintJob.objects.get(facebook_id='some_test_id')
		print_job.sided = JOB_SIDED[0]
		print_job.save()
		self.assertTrue(print_job.sided == JOB_SIDED[0], 'The sided option is not set')

	def test_set_printer_type(self):
		print_job = PrintJob.objects.get(facebook_id='some_test_id')
		print_job.printer_type = PRINTER_TYPE[0]
		print_job.save()
		self.assertTrue(print_job.printer_type == PRINTER_TYPE[0], 'The printer type option is not set')

	def test_set_n_copies(self):
		print_job = PrintJob.objects.get(facebook_id='some_test_id')
		print_job.n_copies = 1
		print_job.save()
		self.assertTrue(print_job.n_copies == 1, 'The num copies option is not set')
