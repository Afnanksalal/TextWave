import requests

FLASK_API_BASE_URL = 'http://your_backend_url'


def process_text(text_input,
                 language='EN',
                 accent='EN-Default',
                 speed=1.0,
                 pitch=0,
                 volume=0,
                 reference_audio=None):
    data = {
        'text_input': text_input,
        'language': language,
        'accent': accent,
        'speed': speed,
        'pitch': pitch,
        'volume': volume,
    }
    files = {}
    if reference_audio:
        files['reference_audio'] = reference_audio

    response = requests.post(f'{FLASK_API_BASE_URL}/process',
                             data=data,
                             files=files)
    return response
