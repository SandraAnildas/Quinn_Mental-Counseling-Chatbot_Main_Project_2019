from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from flask import Flask, Response, Blueprint, request, jsonify
from rasa_core.channels.channel import UserMessage, OutputChannel
from rasa_core.channels.channel import InputChannel
from rasa_core.channels.channel import CollectingOutputChannel
import json	

logger = logging.getLogger(__name__)

		
class GoogleConnector(InputChannel):

	@classmethod
	def name(cls):
		return "google_home"

	def blueprint(self, on_new_message):
		google_webhook = Blueprint('google_webhook', __name__)

		@google_webhook.route("/", methods=['GET'])
		def health():
			return jsonify({"status": "ok"})

		@google_webhook.route("/webhook", methods=['POST'])
		def receive():
			payload = json.loads(request.data)		
			sender_id = payload['user']['userId']
			intent = payload['inputs'][0]['intent'] 			
			text = payload['inputs'][0]['rawInputs'][0]['query'] 		
			if intent == 'actions.intent.MAIN':	
				message = "<speak>Hello! <break time=\"1\"/> This is Quinn here... Your new friend. You can start by saying hi."			 
			else:
				out = CollectingOutputChannel()			
				on_new_message(UserMessage(text, out, sender_id))
				responses = [m["text"] for m in out.messages]
				message = responses[0]	
			r = json.dumps({
				"conversationToken": "{\"state\":null,\"data\":{}}",
				"expectUserResponse": 'true',
				"expectedInputs": [
					{
						"inputPrompt": {
							"initialPrompts": [
								{	
										"ssml": message
								}
							]
						},
						"possibleIntents": [
							{
								"intent": "actions.intent.TEXT"
							}
						]
					}
				]
			})
			return r						
		return google_webhook