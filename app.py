from flask import Flask, request, jsonify
from flask_sockets import Sockets
from elevenlabs.api.tts import TTS, Voice, Model
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import os
import json

app = Flask(__name__)
sockets = Sockets(app)

# Ensure you have the necessary ElevenLabs API key set as an environment variable
os.environ['ELEVEN_API_KEY'] = os.environ["ELEVEN_LABS_API"]

@app.route('/tts', methods=['POST'])
def tts():
    # Extract text from the POST request
    data = request.json
    text = data['text']
    voice_id = data.get('voice_id', '6VOIi9iZnh1UwYhl6DKD')  # Replace with your default voice ID
    model_id = data.get('model_id', 'eleven_monolingual_v2')  # Replace with your default model ID

    # Create Voice and Model objects
    voice = Voice(voice_id=voice_id)
    model = Model(model_id=model_id)

    # Return a response to upgrade to WebSocket
    return jsonify({"message": "Please connect to WebSocket to receive the audio stream."})

@sockets.route('/tts/socket')
def tts_socket(ws):
    # Extract text from WebSocket message
    message = ws.receive()
    data = json.loads(message)
    text = data['text']
    voice_id = data.get('voice_id', '6VOIi9iZnh1UwYhl6DKD')  # Replace with your default voice ID
    model_id = data.get('model_id', 'eleven_monolingual_v2')  # Replace with your default model ID

    # Create Voice and Model objects
    voice = Voice(voice_id=voice_id)
    model = Model(model_id=model_id)

    # Generate audio stream
    audio_stream = TTS.generate_stream_input(
        text=text,
        voice=voice,
        model=model,
        api_key=os.environ.get('ELEVEN_API_KEY')
    )

    # Send audio stream back through WebSocket
    for audio_chunk in audio_stream:
        ws.send(audio_chunk)

if __name__ == '__main__':


    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    print("Server listening on: http://127.0.0.1:5000")
    server.serve_forever()