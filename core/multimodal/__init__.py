"""
Мультимодальные компоненты для Dual Qwen Brain
TTS, Vision и другие модальности
"""
from .tts import GPTSoVITSTTS, TTSManager

__all__ = [
    "GPTSoVITSTTS",
    "TTSManager"
]
