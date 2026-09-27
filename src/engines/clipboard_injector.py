import time
import logging
import pyperclip
from pynput.keyboard import Controller, Key

from src.contracts.text_injector import ITextInjector

logger = logging.getLogger(__name__)


class ClipboardInjector(ITextInjector):
    """
    Motor de injeção de texto utilizando área de transferência e simulação de teclado.
    Usa pynput para simular Ctrl+V de forma confiável no Windows.
    """

    def __init__(self) -> None:
        self._keyboard = Controller()

    def inject(self, text: str) -> None:
        """
        Injeta o texto copiando-o para a área de transferência e simulando 'Ctrl+V'.
        Restabelece o clipboard original em seguida.

        :param text: O texto a ser injetado/colado.
        """
        if not text:
            logger.warning("Texto vazio fornecido. Injeção abortada.")
            return

        logger.info(f"Iniciando injeção de texto ({len(text)} caracteres)...")

        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            logger.warning("Falha ao ler clipboard original. Assumindo vazio.")
            original_clipboard = ""

        try:
            pyperclip.copy(text)

            # Simula Ctrl+V usando pynput
            self._keyboard.press(Key.ctrl)
            self._keyboard.press('v')
            self._keyboard.release('v')
            self._keyboard.release(Key.ctrl)

            time.sleep(0.15)
            logger.info("Texto injetado com sucesso via Ctrl+V.")

        except Exception as e:
            logger.error(f"Erro durante a injeção: {e}")
            raise
        finally:
            try:
                pyperclip.copy(original_clipboard)
                logger.debug("Clipboard original restaurado.")
            except Exception as e:
                logger.error(f"Erro ao restaurar clipboard: {e}")
