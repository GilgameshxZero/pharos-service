import json, requests
from pprint import pprint

from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from messprint.models import PrintJob, PrintUserState, NEXT_STATE_RESPONSE
from messprint.pharos_print import print_file_from_url

# Create your views here
class PrintView(generic.View):

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return generic.View.dispatch(self, request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		print(self.request.GET)
		if self.request.GET.get('hub.verify_token') == '2318934571':
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('Hello World')

	# # POST function to handle Facebook messages
	# def post(self, request, *args, **kwargs):
	#     # Converts the text payload into a python dictionary
	#     incoming_message = json.loads(self.request.body.decode('utf-8'))
	#     # Facebook recommends going through every entry since they might send
	#     # multiple messages in a single call during high load
	#     for entry in incoming_message['entry']:
	#         for message in entry['messaging']:
	#             # Check to make sure the received call is a message call
	#             # This might be delivery, optin, postback for other events
	#             if 'message' in message:
	#                 # Print the message to the terminal
	#                 pprint(message)
	#                 post_facebook_message(message['sender']['id'], message['message']['text'])
	#     return HttpResponse()

	def _handle_pdf(self, sender_id, message_data):
		if message_data['attachments']['type'] != 'file':
			return 'Sorry. We only support printing files. :/'

		sender_state_exists = PrintUserState.objects.filter(facebook_id = sender_id).exists()
		if sender_state_exists: # reset current print job and let the user start with another one
			sender_state = PrintUserState.objects.get(facebook_id = sender_id)
			sender_state.state = 'P'
			sender_state.save()
		else:
			pdf_url = message_data['attachments']['payload']['url']
			sender_state = PrintUserState.objects.create(facebook_id = sender_id, state = 'P')
			sender_print_job = PrintJob.objects.create(facebook_id = sender_id, pdf_url = pdf_url)
		return NEXT_STATE_RESPONSE['P']

	def _fetch_sender_data(self, sender_id):
		sender_state = PrintUserState.objects.get(facebook_id = sender_id)
		sender_print_job = PrintJob.objects.get(facebook_id = sender_id)
		return (sender_state, sender_print_job)

	def _handle_kerberos(self, sender_id, message_data):
		sender_state, sender_print_job = self._fetch_sender_data(sender_id)

		sender_state.state = 'K'
		sender_print_job.kerberos = message_data['text']
		sender_state.save()
		sender_print_job.save()
		return NEXT_STATE_RESPONSE['K']

	def _handle_sided(self, sender_id, message_data):
		sender_state, sender_print_job = self._fetch_sender_data(sender_id)

		sender_state.state = 'S'
		sender_print_job.sided = 'S' if message_data['text'] == 'single' else 'D'
		sender_state.save()
		sender_print_job.save()
		return NEXT_STATE_RESPONSE['S']

	def _handle_printer_type(self, sender_id, message_data):
		sender_state, sender_print_job = self._fetch_sender_data(sender_id)

		sender_state.state = 'T'
		sender_print_job.printer_type = 'B' if message_data['text'] == 'bw' else 'C'
		sender_state.save()
		sender_print_job.save()
		return NEXT_STATE_RESPONSE['T']

	def _handle_n_copies(self, sender_id, message_data):
		sender_state, sender_print_job = self._fetch_sender_data(sender_id)

		try:
			n_copies = int(message_data['text'])
		except ValueError:
			return 'Please insert a valid number of copies'

		sender_state.state = 'N'
		sender_print_job.n_copies = n_copies
		sender_state.save()
		sender_print_job.save()

		print('At the end {}'.format(sender_print_job))
  #   	print_file_from_url(
  #   		sender_print_job.pdf_url,
  #   		sender_print_job.kerberos,
  #   		'mit-print.pdf',
  #   		color = sender_print_job.printer_type == 'C',
  #   		double_sided = sender_print_job.sided == 'D',
  #   		n_copies = sender_print_job.n_copies
	# )

		sender_state.delete()
		sender_print_job.delete()
		return NEXT_STATE_RESPONSE['N']

    # POST 2.0
    def post(self, request, *args, **kwargs):
        incoming_data = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_data['entry']:
            messaging_data = entry['messaging'][0]
            if 'message' not in messaging_data:
                continue

            sender_id = messaging_data['sender']['id']
            try: # should only exist after the user created a print job
                sender_state = PrintUserState.objects.get(facebook_id = sender_id)
            except PrintUserState.DoesNotExist:
                sender_state = None

            message_data = messaging_data['message']
            if 'attachments' in message_data:
                response_text = self._handle_pdf(sender_id, message_data)
            elif not sender_state:
                response_text = 'Please send a valid PDF.'
            elif sender_state.state == 'P':
                response_text = self._handle_kerberos(sender_id, message_data)
            elif sender_state.state == 'K':
                response_text = self._handle_sided(sender_id, message_data)
            elif sender_state.state == 'S':
                response_text = self._handle_printer_type(sender_id, message_data)
            else: # sender_state.state == 'T':
                response_text = self._handle_n_copies(sender_id, message_data)

            post_facebook_message(sender_id, response_text)
            return HttpResponse()

def post_facebook_message(recipient_id, received_message):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHAxr1y4u0BAFMTj3WsZCe9xjca9E3wO4K2Dj8JQpN1FghKWTZBmFwbgcpz0IWiG0G5XsoHfHwysQBcKZB3nVYJ6kC7JQm0oq5iqQLPA13AZBe97bsJi9UKxZAzE9LMRSb1ZA78zVAx9E6nminB8nZBAoIHpZBhoZCR9QSOdvRWzbviogqA0hV44'
	response_msg = json.dumps({"recipient" : {"id" : recipient_id}, "message": {"text" : received_message}})
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data = response_msg)
	# pprint(status.json())
