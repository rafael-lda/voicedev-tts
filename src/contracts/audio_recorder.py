from abc import ABC, abstractmethod

class IAudioRecorder(ABC):
    """Interface abstrata para captura de áudio do microfone."""

    @abstractmethod
    def start_recording(self) -> None:
        """Inicia a gravação de áudio."""
        ...

    @abstractmethod
    def stop_recording(self) -> bytes:
        """Para a gravação e retorna os bytes de áudio capturados."""
        ...

    @abstractmethod
    def is_recording(self) -> bool:
        """Retorna True se está gravando."""
        ...
