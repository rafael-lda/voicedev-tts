from abc import ABC, abstractmethod

class IAudioPlayer(ABC):
    """Interface abstrata para reprodução de áudio."""

    @abstractmethod
    def play(self, audio_bytes: bytes) -> None:
        """Reproduz dados de áudio."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Interrompe a reprodução em andamento."""
        ...

    @abstractmethod
    def pause(self) -> None:
        """Pausa a reprodução atual."""
        ...

    @abstractmethod
    def unpause(self) -> None:
        """Retoma a reprodução pausada."""
        ...

    @abstractmethod
    def is_playing(self) -> bool:
        """Retorna True se há áudio sendo reproduzido."""
        ...
