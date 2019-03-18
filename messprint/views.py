from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests
from pprint import pprint

from messprint.models import PrintJob
from messprint.pharos_print import print_file_from_url

# Create your views here.# def first(request):
#     return HttpResponse('Hey this works')

class PrintView(generic.View):
    def get(self, request, *args, **kwargs):
        print(self.request.GET)
        if self.request.GET.get('hub.verify_token') == '2318934571':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Hello World')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        print("HELLO WORLDDDD")
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()

def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHAxr1y4u0BAFMTj3WsZCe9xjca9E3wO4K2Dj8JQpN1FghKWTZBmFwbgcpz0IWiG0G5XsoHfHwysQBcKZB3nVYJ6kC7JQm0oq5iqQLPA13AZBe97bsJi9UKxZAzE9LMRSb1ZA78zVAx9E6nminB8nZBAoIHpZBhoZCR9QSOdvRWzbviogqA0hV44'
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())
