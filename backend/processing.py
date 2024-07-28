import librosa
import numpy as np 

def adjust_pitch(audio_data, sample_rate, semitones):
    """Adjusts the pitch using Librosa with high-quality resampling."""
    pitched_data = librosa.effects.pitch_shift(
        audio_data,
        sr=sample_rate,
        n_steps=semitones,
        res_type='soxr_hq'  # Use high-quality resampling
    )
    return pitched_data

def adjust_volume(audio_data, decibels):
    """Adjusts the volume of the audio data using Librosa."""

    amp_ratio = 10 ** (decibels / 20.0)
    adjusted_data = audio_data * amp_ratio
    return adjusted_data