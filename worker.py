"""
This module contains functions to interact with IBM Watson services for speech-to-text, 
text-to-speech, and language translation using the watsonx API Functions:      
"""

import requests

# To call watsonx's LLM, we need to import the library of IBM watsonx.ai
#from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import ModelInference
# Define the model parameters
#from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
#from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

# Watsonx_API and Project_id incase you need to use the code outside this environment
# API_KEY = "Your WatsonX API"
PROJECT_ID= "skills-network"

# Define the credentials
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com"
    # api_key=API_KEY
)

# Specify model_id that will be used for inferencing
MODEL_ID = "mistralai/mistral-medium-2505"

parameters = TextChatParameters(
    temperature=0,
    max_tokens=1024
)

# Define the LLM

model = ModelInference(
    model_id=MODEL_ID,
    params=parameters,
    credentials=credentials,
    project_id=PROJECT_ID
)



def speech_to_text(audio_binary):
    """
    This function takes an audio binary input and sends it to the Watson Speech-to-Text service 
    for transcription. It returns the transcribed text as a string.
    """
    # Set up Watson Speech-to-Text HTTP Api url
    base_url = 'https://sn-watson-stt.labs.skills.network'
    api_url = base_url+'/speech-to-text/api/v1/recognize'

	# Set up parameters for our HTTP reqeust
    params = {
		'model': 'en-US_Multimedia',
	}

    # Set up the body of our HTTP request
    body = audio_binary

	# Send a HTTP Post request
    response = requests.post(api_url, params=params, data=body, timeout=30).json()

	# Parse the response to get our transcribed text
    text = 'null'
    while bool(response.get('results')):
        print('Speech-to-Text response:', response)
        text = response.get('results').pop().get('alternatives').pop().get('transcript')
        print('recognised text: ', text)
        return text

def text_to_speech(text, voice=""):
    """
    This function takes a text input and sends it to the Watson Text-to-Speech service
    for audio synthesis. It returns the synthesized audio as a binary.
    """
    # Set up Watson Text-to-Speech HTTP Api url
    base_url = 'https://sn-watson-tts.labs.skills.network'
    api_url = base_url + '/text-to-speech/api/v1/synthesize?output=output_text.wav'

	# Adding voice parameter in api_url if the user has selected a preferred voice
    if voice not in ["", "default"]:
        api_url += "&voice=" + voice

    # Set the headers for our HTTP request
    headers = {
        'Accept': 'audio/wav',
        'Content-Type': 'application/json',
    }

    # Set the body of our HTTP request
    json_data = {
        'text': text,
    }

    # Send a HTTP Post reqeust to Watson Text-to-Speech Service
    response = requests.post(api_url, headers=headers, json=json_data, timeout=30)
    print('Text-to-Speech response:', response)
    return response.content


def watsonx_process_message(user_message):
    """
    This function takes a user message as input and sends it to the Watsonx LLM for
    processing. It returns the response from the model as a string.
    """
    prompt = f"""
    Translate the following English sentence into Spanish.
    Reply ONLY with the translation, no explanations, no formatting, no extra text.
    English: {user_message}
    Spanish:
    """
    messages = [{"role": "user", "content": prompt}]
    response = model.chat(messages=messages)
    response_text = response["choices"][0]["message"]["content"]
    print("watsonx response:", response_text)
    return response_text.strip()
