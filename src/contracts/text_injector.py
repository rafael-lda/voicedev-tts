from abc import ABC, abstractmethod

class ITextInjector(ABC):
    """Interface abstrata para injeção de texto no editor."""

    @abstractmethod
    def inject(self, text: str) -> None:
        """Injeta texto no campo de entrada ativo."""
        ...
