import os
import torch
import logging
from tempfile import NamedTemporaryFile

import librosa  # For audio loading and processing 
import soundfile as sf  

from openvoice import se_extractor
from melo.api import TTS 

logger = logging.getLogger(__name__)

def load_tone_color_converter(ckpt_converter, device):
    """Loads the Tone Color Converter model."""
    from openvoice.api import ToneColorConverter 
    try:
        tone_color_converter = ToneColorConverter(os.path.join(ckpt_converter, 'config.json'), device=device)
        tone_color_converter.load_ckpt(os.path.join(ckpt_converter, 'checkpoint.pth'))
        return tone_color_converter
    except FileNotFoundError:
        raise FileNotFoundError("Converter files not found")
    except Exception as e:
        raise Exception(f"Error loading ToneColorConverter: {e}")


def extract_speaker_embedding(uploaded_file, tone_color_converter):
    """Extracts speaker embedding from the uploaded audio."""
    logger.info("Reference audio detected")
    try:
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            uploaded_file.save(temp_file_path)
            logger.info(f"Audio saved to: {temp_file_path}")

            try:
                target_se, _ = se_extractor.get_se(temp_file_path, tone_color_converter, vad=False)
                logger.info(f"Speaker embedding extracted: {target_se is not None}")
                return target_se
            except Exception as e:
                logger.error(f"Embedding extraction error: {e}")
                raise Exception(f"Embedding extraction error: {e}")

    except Exception as e:
        logger.error(f"Audio handling error: {e}")
        raise Exception(f"Audio handling failed: {e}")

def generate_audio_segment(sentence, language, accent, speed, device,
                            tone_color_converter, target_se):
    """Generates an audio segment for the sentence."""
    try:
        logger.info(f"Loading TTS model for: {language}")
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id
        logger.info(f"Available speakers: {speaker_ids}")

        source_se = load_source_speaker_embedding(language, accent, speaker_ids, device)
        spkr = choose_speaker(language, accent, speaker_ids)

        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
            output_wav_path = temp_audio_file.name
            model.tts_to_file(sentence, spkr, output_wav_path, speed=speed)

            # Load audio using Librosa
            audio_data, sample_rate = librosa.load(output_wav_path)

            if target_se is not None:
                apply_voice_cloning(output_wav_path, source_se, target_se, tone_color_converter)

                # Reload audio after voice cloning
                audio_data, _ = librosa.load(output_wav_path) 

            return audio_data, sample_rate 

    except Exception as e:
        logger.error(f"Error generating audio for sentence: {e}")
        raise Exception(f"Audio generation failed for sentence: {e}")

def load_source_speaker_embedding(language, accent, speaker_ids, device):
    """Loads the correct speaker embedding."""
    if language == 'EN':
        try:
            speaker_file = f'{accent.lower().replace("_", "-")}.pth'
            source_se = torch.load(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checkpoint', 'base_speakers', 'ses', speaker_file),
                map_location=device
            )
            logger.info("Using default speaker embedding")
            return source_se
        except Exception as e:
            logger.error(f"Failed to load default speaker embedding: {e}")
            raise Exception("Failed to load default speaker embedding")
    else:
        return torch.randn((1, 256, 1))  

def choose_speaker(language, accent, speaker_ids):
    """Chooses the speaker based on language and accent."""
    if language == 'EN':
        available_accents = list(speaker_ids.keys())
        if accent in available_accents:
            return speaker_ids[accent]
        else:
            logger.warning(f"Accent '{accent}' not found. Using the first available accent.")
            return list(speaker_ids.values())[0]
    else:
        return list(speaker_ids.values())[0] 

def apply_voice_cloning(output_wav_path, source_se, target_se, tone_color_converter):
    """Applies voice cloning to the generated audio."""
    try:
        tone_color_converter.convert(
            audio_src_path=output_wav_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_wav_path
        )
        logger.info("Applied voice cloning")
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        raise Exception(f"Voice cloning error: {e}")