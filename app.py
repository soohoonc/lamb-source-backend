from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from elevenlabs.api.tts import TTS, Voice, Model
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import os
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return 'Hello World!'

# Ensure you have the necessary ElevenLabs API key set as an environment variable
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

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

# @socketio.on('connect')
# def test_socket(ws):
#     print("test websocket")
#     try:
#         while not ws.closed:
#             message = ws.receive()
#             if message:
#                 print("Received message from VS Code:", message)
#     except Exception as e:
#         print("Exception in test_socket:", e)

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

# if __name__ == '__main__':
#     server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
#     print("Server listening on: http://127.0.0.1:5000")
#     socketio.run(app)

if __name__ == '__main__':
    socketio.run(app)