from abc import ABC, abstractmethod

class ISpeechRecognizer(ABC):
    """Interface abstrata para motores de reconhecimento de voz (STT)."""

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Transcreve bytes de áudio em texto."""
        ...
