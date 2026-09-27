"""
Módulo de contratos (interfaces) do projeto VoiceDev.
Exporta as interfaces para os componentes do sistema.
"""

from .speech_synthesizer import ISpeechSynthesizer
from .speech_recognizer import ISpeechRecognizer
from .audio_player import IAudioPlayer
from .audio_recorder import IAudioRecorder
from .text_injector import ITextInjector

__all__ = [
    "ISpeechSynthesizer",
    "ISpeechRecognizer",
    "IAudioPlayer",
    "IAudioRecorder",
    "ITextInjector",
]
