from abc import ABC, abstractmethod

class ISpeechSynthesizer(ABC):
    """Interface abstrata para motores de síntese de voz (TTS)."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Converte texto em bytes de áudio."""
        ...
