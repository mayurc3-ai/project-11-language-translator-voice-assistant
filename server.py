"""
This module contains the Flask server implementation for handling speech-to-text, 
text-to-speech, and message processing requests. It defines routes for the web application 
and interacts with the worker functions to perform the necessary operations. The server listens
 for incoming requests, processes them using the worker functions, and returns the appropriate 
 responses
"""

import os
import base64
import json
from flask import Flask, render_template, request
from flask_cors import CORS
from worker import speech_to_text, text_to_speech, watsonx_process_message

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def index():
    """
    Render the index.html template for the root route.
    """
    return render_template('index.html')


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    """
    Handle the speech-to-text route. This route receives an audio binary input from the user
    and calls the speech_to_text function to transcribe the speech into text. The transcribed 
    text is then returned to the user in JSON format.
    """
    print("processing Speech-to-Text")
    audio_binary = request.data # Get the user's speech from their request
    text = speech_to_text(audio_binary) # Call speech_to_text function to transcribe the speech

	# Return the response to user in JSON format
    response = app.response_class(
        response=json.dumps({'text': text}),
        status=200,
        mimetype='application/json'
    )
    print(response)
    print(response.data)
    return response



@app.route('/process-message', methods=['POST'])
def process_message_route():
    """
    Handle the process-message route. This route receives a user message and an optional
    preferred voice from the user. It calls the watsonx_process_message function to process
    the user's message and get a response back. The response is then converted to speech using
    the text_to_speech function, and both the text and speech responses are returned to the
    user in JSON format.
    """
    user_message = request.json['userMessage'] # Get user's message from their request
    print('user_message', user_message)

    voice = request.json['voice'] # Get user\'s preferred voice from their request
    print('voice', voice)

	# Call watsonx_process_message function to process the user's message and get a response back
    watsonx_response_text = watsonx_process_message(user_message)

	# Clean the response to remove any emptylines
    watsonx_response_text = os.linesep.join([s for s in watsonx_response_text.splitlines() if s])

	# Call our text_to_speech function to convert Watsonx Api's reponse to speech
    watsonx_response_speech = text_to_speech(watsonx_response_text, voice)

    # convert watsonx_response_speech to base64 string so it can be sent back in the JSON response
    watsonx_response_speech = base64.b64encode(watsonx_response_speech).decode('utf-8')

	# Send a JSON response back to the user containing their message\'s response both in text
    # and speech formats
    response = app.response_class(
        response=json.dumps({"watsonxResponseText": watsonx_response_text,
                             "watsonxResponseSpeech": watsonx_response_speech}),
        status=200,
        mimetype='application/json'
    )

    print(response)
    return response



if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0')
