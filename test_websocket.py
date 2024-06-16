import asyncio
import websockets
import json
import base64
from dotenv import load_dotenv
from master_ozz.utils import ozz_master_root
# from openai import AsyncOpenAI
import os

load_dotenv(os.path.join(ozz_master_root(),'.env'))

async def text_to_speech(voice_id):
    model = 'eleven_monolingual_v1' # eleven_multilingual_v2, eleven_turbo_v2
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model}"

    async with websockets.connect(uri) as websocket:

        # Initialize the connection
        bos_message = {
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            },
            "xi_api_key": os.environ.get("api_elevenlabs"),  # Replace with your API key
        }
        await websocket.send(json.dumps(bos_message))

        # Send "Hello World" input
        input_message = {
            "text": "It's story time lets tell a story ",
            "try_trigger_generation": True
        }
        await websocket.send(json.dumps(input_message))

        # Send EOS message with an empty string instead of a single space
        # as mentioned in the documentation
        eos_message = {
            "text": ""
        }
        await websocket.send(json.dumps(eos_message))

        # Added a loop to handle server responses and print the data received
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print("Server response:", data)

                if data["audio"]:
                    chunk = base64.b64decode(data["audio"])
                    print("Received audio chunk")
                else:
                    print("No audio data in the response")
                    break
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

asyncio.get_event_loop().run_until_complete(text_to_speech("21m00Tcm4TlvDq8ikWAM"))