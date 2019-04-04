import json
import re
import requests
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
            return HttpResponse('Hello world!')

    def _handle_pdf(self, sender_id, message_data):
        sender_state_exists = PrintUserState.objects.filter(
            facebook_id=sender_id).exists()
        response = ''
        pdf_url = ''

        if 'text' in message_data and re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_data['text']):
            pdf_url = message_data['text']
        else:
            pdf_url = message_data['attachments'][0]['payload']['url']

        r = requests.get(pdf_url)
        content_type = r.headers.get('content-type')

        # not a pdf
        if not 'application/pdf' in content_type:
            response += 'We don\'t officially support printing this file format (non-PDF). However, we\'ll try our best anyway ^_^\n\n'

        if sender_state_exists:  # reset current print job and let the user start with another one
            sender_state, sender_print_job = self._fetch_sender_data(sender_id)
            sender_state.state = 'P'
            sender_print_job.pdf_url = pdf_url
        else:
            sender_state = PrintUserState.objects.create(
                facebook_id=sender_id, state='P')
            sender_print_job = PrintJob.objects.create(
                facebook_id=sender_id, pdf_url=pdf_url)
        sender_state.save()
        sender_print_job.save()
        return response + NEXT_STATE_RESPONSE['P']

    def _fetch_sender_data(self, sender_id):
        sender_state = PrintUserState.objects.get(facebook_id=sender_id)
        sender_print_job = PrintJob.objects.get(facebook_id=sender_id)
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

        if message_data['text'] != 'single' and message_data['text'] != 'double':
            return 'Please type "single" or "double".'

        sender_state.state = 'S'
        sender_print_job.sided = 'S' if message_data['text'] == 'single' else 'D'
        sender_state.save()
        sender_print_job.save()
        return NEXT_STATE_RESPONSE['S']

    def _handle_printer_type(self, sender_id, message_data):
        sender_state, sender_print_job = self._fetch_sender_data(sender_id)

        if message_data['text'] != 'bw' and message_data['text'] != 'color':
            return 'Please type "bw" or "color".'

        sender_state.state = 'T'
        sender_print_job.printer_type = 'C' if message_data['text'] == 'color' else 'B'
        sender_state.save()
        sender_print_job.save()
        return NEXT_STATE_RESPONSE['T']

    def _handle_n_copies(self, sender_id, message_data):
        sender_state, sender_print_job = self._fetch_sender_data(sender_id)

        try:
            n_copies = int(message_data['text'])
        except ValueError:
            return 'Please input a valid integer (of copies).'

        sender_state.state = 'N'
        sender_print_job.n_copies = n_copies
        sender_state.save()
        sender_print_job.save()

        print('At the end {}'.format(sender_print_job))
        print_file_from_url(
            sender_print_job.pdf_url,
            sender_print_job.kerberos,
            '[MIT Mobile Print] ' + sender_print_job.pdf_url.split('/')[-1],
            color=sender_print_job.printer_type == 'C',
            double_sided=sender_print_job.sided == 'D',
            n_copies=sender_print_job.n_copies
        )

        sender_state.delete()
        sender_print_job.delete()
        return NEXT_STATE_RESPONSE['N']

    # POST 2.0
    def post(self, request, *args, **kwargs):
        incoming_data = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_data)
        for entry in incoming_data['entry']:
            try:
                messaging_data = entry['messaging'][0]
                if 'message' not in messaging_data:
                    return HttpResponse()

                sender_id = messaging_data['sender']['id']
                try:  # should only exist after the user created a print job
                    sender_state = PrintUserState.objects.get(
                        facebook_id=sender_id)
                except PrintUserState.DoesNotExist:
                    sender_state = None

                message_data = messaging_data['message']
                if 'text' in message_data and message_data['text'] == "ios":
                    response_text = 'On iOS, to print a PDF blocked behind Stellar:\n1. Open the PDF in Safari (in Chrome, simply tap the PDF, select "Open In..." and skip to step 4)\n2. Tap the "Forward" button\n3. Scroll right in the bottom row and click "Create PDF"\n4. Share the file with yourself in Facebook Messenger with the button in the bottom left (if messenger is not an option, click "more" and add it as an option).\n5. In Messenger, click the file you sent to yourself to open it and copy its link using the top-right button.\n6. Paste the link here!\n\nWe don\'t officially support printing file formats other than PDF, but you may still send such a file, and we\'ll try our best.'
                elif 'text' in message_data and message_data['text'] == "andriod":
                    response_text = 'On Andriod, there is no built-in way to print using MIT Mobile Print. However, if you\'re able to generate a web-accessible link to the PDF, pasting the link here will work.\n\nWe don\'t officially support printing file formats other than PDF, but you may still send such a file, and we\'ll try our best.'
                elif ('text' in message_data and re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_data['text'])) or 'attachments' in message_data:
                    print('attachment handler firing')
                    response_text = self._handle_pdf(sender_id, message_data)
                elif not sender_state:
                    print('no valid sender state')
                    response_text = 'Paste a PDF link or attach a PDF file to get started.\n\nFor further instructions, message "ios" or "android".'
                elif sender_state.state == 'P':
                    print('kerb handler')
                    response_text = self._handle_kerberos(
                        sender_id, message_data)
                elif sender_state.state == 'K':
                    print('sided handler')
                    response_text = self._handle_sided(sender_id, message_data)
                elif sender_state.state == 'S':
                    print('color handler')
                    response_text = self._handle_printer_type(
                        sender_id, message_data)
                else:  # sender_state.state == 'T':
                    print('copies handler')
                    response_text = self._handle_n_copies(
                        sender_id, message_data)

                post_facebook_message(sender_id, response_text)
            except:
                post_facebook_message(
                    sender_id, 'Error while processing message.')
                print('error while processing message')
            return HttpResponse()


def post_facebook_message(recipient_id, received_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHAxr1y4u0BAFMTj3WsZCe9xjca9E3wO4K2Dj8JQpN1FghKWTZBmFwbgcpz0IWiG0G5XsoHfHwysQBcKZB3nVYJ6kC7JQm0oq5iqQLPA13AZBe97bsJi9UKxZAzE9LMRSb1ZA78zVAx9E6nminB8nZBAoIHpZBhoZCR9QSOdvRWzbviogqA0hV44'
    response_msg = json.dumps(
        {"recipient": {"id": recipient_id}, "message": {"text": received_message}})
    status = requests.post(post_message_url, headers={
                           "Content-Type": "application/json"}, data=response_msg)
    # pprint(status.json())
