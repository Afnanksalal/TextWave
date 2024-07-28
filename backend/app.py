import io
import os
import time
import logging
from tempfile import NamedTemporaryFile

import numpy as np  # For audio concatenation
import soundfile as sf # For writing audio with Librosa
from flask import Flask, request, jsonify, send_file

# Import custom modules
from ratelimit import rate_limit, RateLimitExceededError
from translation import translation_pipelines
from processing import adjust_pitch, adjust_volume
from handling import (
    load_tone_color_converter,
    extract_speaker_embedding,
    generate_audio_segment
)

# Suppress warnings - consider making this configurable 
import warnings
warnings.filterwarnings("ignore")
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('torch').setLevel(logging.ERROR)
logging.getLogger('faster_whisper').setLevel(logging.ERROR)
logging.getLogger('libav.mp3').setLevel(logging.ERROR)

# App initialization
app = Flask(__name__)

# Custom logging setup
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_colors = {
            'DEBUG': "\033[94m",
            'INFO': "\033[92m",
            'WARNING': "\033[93m",
            'ERROR': "\033[91m",
            'CRITICAL': "\033[95m"
        }
        reset_color = "\033[0m"
        log_emojis = {
            'DEBUG': "🔍",
            'INFO': "ℹ️",
            'WARNING': "⚠️",
            'ERROR': "❌",
            'CRITICAL': "‼️"
        }
        log_msg = super().format(record)
        color = log_colors.get(record.levelname, "")
        emoji = log_emojis.get(record.levelname, "")
        formatted_msg = f"{color}{emoji} {log_msg}{reset_color}"
        return formatted_msg

formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Global vars 
ckpt_converter = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checkpoint', 'converter')
device = "cpu" 

@app.route('/', methods=['GET'])
def api_alive():
    """Endpoint to check if the API is alive."""
    return jsonify({
        "message": "API is alive",
        "schema": {
            "text_input": "Text to process (required)",
            "language": "Target language ('ES', 'FR', 'ZH', 'JP', default: 'EN')",
            "accent": "Accent for English ('US', 'BR', 'INDIA', 'AU', default: 'EN-Default')",
            "speed": "Speech speed multiplier (default: 1.0)",
            "pitch": "Pitch shift in semitones (default: 0)",
            "volume": "Volume adjustment in dB (default: 0)",
            "reference_audio": "Audio file (MP3/WAV) for voice cloning"
        }
    }), 200

@app.route('/process', methods=['POST'])
def process_request():
    """Main endpoint to process text and generate audio."""
    try:
        # Rate limiting
        rate_limit(request.remote_addr, 50, 3600)  

        # Get request parameters
        text_input = request.form.get('text_input', '')
        language = request.form.get('language', 'EN').upper()
        accent = request.form.get('accent', 'EN-Default')
        speed = float(request.form.get('speed', 1.0))
        pitch = int(request.form.get('pitch', 0))
        volume = int(request.form.get('volume', 0))
        uploaded_file = request.files.get('reference_audio')

        logger.info(f"Request: Text='{text_input}', Language='{language}', Accent='{accent}'")

        # Initialize Tone Color Converter
        try:
            tone_color_converter = load_tone_color_converter(ckpt_converter, device)
            logger.info("Tone color converter loaded")
        except Exception as e:
            logger.error(f"Error loading ToneColorConverter: {e}")
            return jsonify({'error': f"Converter initialization failed: {e}"}), 500

        # Extract speaker embedding
        target_se = None
        if uploaded_file:
            target_se = extract_speaker_embedding(uploaded_file, tone_color_converter)

        # Translate text
        if language != 'EN':
            translator = translation_pipelines.get(language)
            if translator:
                text_input = translator(text_input, max_length=512)[0]['translation_text'] 
                logger.info(f"Translated text: {text_input}")
            else:
                logger.error(f"Unsupported language: {language}")
                return jsonify({'error': f"Unsupported language: {language}"}), 400 

        # Generate audio segments
        audio_segments = []
        sentences = text_input.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                try:
                    audio_segment, sample_rate = generate_audio_segment(
                        sentence, language, accent, speed, device,
                        tone_color_converter, target_se
                    )
                    if audio_segment is not None: 
                        audio_segment = adjust_pitch(audio_segment, sample_rate, pitch)
                        audio_segment = adjust_volume(audio_segment, volume)
                        audio_segments.append((audio_segment, sample_rate)) 

                except Exception as e:
                    logger.error(f"Error generating audio for sentence: {e}")
                    return jsonify({'error': f"Audio generation failed for a sentence: {e}"}), 500

        # Combine audio using Librosa
        if audio_segments:
            combined_audio = None
            for segment, sr in audio_segments:
                if combined_audio is None:
                    combined_audio = segment
                    combined_sr = sr  
                else:
                    # Resample if sample rates don't match
                    if sr != combined_sr:
                        segment = librosa.resample(segment, orig_sr=sr, target_sr=combined_sr)
                    combined_audio = np.concatenate((combined_audio, segment))

            # Export the combined audio
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                output_wav_path = temp_audio_file.name
                sf.write(output_wav_path, combined_audio, combined_sr, 'PCM_24') 

                with open(output_wav_path, 'rb') as faudio:
                    return send_file(
                        io.BytesIO(faudio.read()),
                        mimetype='audio/wav',
                        as_attachment=True,
                        download_name='combined_audio.wav'
                    )
        else:
            return jsonify({'error': "No audio segments generated"}), 500

    except RateLimitExceededError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        return jsonify({'error': str(e), 'time_to_wait': e.time_to_wait, 'current_requests': e.current_requests}), 429
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': f"Unexpected error: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)