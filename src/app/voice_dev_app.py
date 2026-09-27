import asyncio
import logging
import pyperclip
from pynput.keyboard import Controller as KeyboardController, Key
from typing import Callable, Optional

from src.contracts import (
    ISpeechSynthesizer,
    ISpeechRecognizer,
    IAudioPlayer,
    IAudioRecorder,
    ITextInjector
)

logger = logging.getLogger(__name__)


class VoiceDevApp:
    """
    Orquestrador principal das funcionalidades de voz.
    Depende apenas de interfaces (injeção de dependência).
    """

    def __init__(
        self,
        synthesizer: ISpeechSynthesizer,
        recognizer: ISpeechRecognizer,
        player: IAudioPlayer,
        recorder: IAudioRecorder,
        injector: ITextInjector
    ) -> None:
        self._synthesizer = synthesizer
        self._recognizer = recognizer
        self._player = player
        self._recorder = recorder
        self._injector = injector
        self._kb = KeyboardController()

        self._status: str = 'idle'
        self.on_status_changed: Optional[Callable[[str], None]] = None

    @property
    def status(self) -> str:
        """Retorna o status atual da aplicação."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Atualiza o status e notifica o callback, se houver."""
        if self._status != value:
            self._status = value
            logger.info(f"Status alterado para: {value}")
            if self.on_status_changed:
                self.on_status_changed(value)

    async def speak(self, text: str) -> None:
        """Sintetiza texto via TTS e reproduz. Se já estiver tocando, para antes."""
        if not text or not text.strip():
            logger.warning("Texto vazio, nada a sintetizar.")
            return

        if self._player.is_playing():
            logger.info("Parando áudio em reprodução atual.")
            self._player.stop()

        try:
            self.status = 'synthesizing'
            audio_bytes = await self._synthesizer.synthesize(text)

            self.status = 'playing'
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._player.play, audio_bytes)
        except Exception as e:
            logger.error(f"Erro ao sintetizar ou reproduzir áudio: {e}")
        finally:
            self.status = 'idle'

    def toggle_recording(self) -> None:
        """
        Alterna gravação: se não está gravando, inicia.
        Se está gravando, para, transcreve e injeta o texto no editor.
        """
        if self._recorder.is_recording():
            logger.info("Finalizando gravação via toggle...")
            try:
                audio_data = self._recorder.stop_recording()
                self.status = 'transcribing'

                text = self._recognizer.transcribe(audio_data)
                if text and text.strip():
                    logger.info(f"Texto transcrito: {text}")
                    self._injector.inject(text)
                else:
                    logger.warning("Nenhum texto reconhecido para injetar.")
            except Exception as e:
                logger.error(f"Erro ao processar gravação: {e}")
            finally:
                self.status = 'idle'
        else:
            logger.info("Iniciando gravação via toggle...")
            try:
                self._recorder.start_recording()
                self.status = 'recording'
            except Exception as e:
                logger.error(f"Erro ao iniciar gravação: {e}")
                self.status = 'idle'

    async def speak_clipboard(self) -> None:
        """Obtém texto do clipboard e fala."""
        try:
            text = pyperclip.paste()
            if text:
                await self.speak(text)
            else:
                logger.warning("Clipboard vazio.")
        except Exception as e:
            logger.error(f"Erro ao ler clipboard: {e}")

    async def speak_selection(self) -> None:
        """Simula Ctrl+C, pega texto do clipboard e fala. Restaura clipboard original depois."""
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        try:
            self._kb.press(Key.ctrl)
            self._kb.press('c')
            self._kb.release('c')
            self._kb.release(Key.ctrl)
            await asyncio.sleep(0.15)

            text = pyperclip.paste()
            if text and text != old_clipboard:
                await self.speak(text)
            else:
                logger.warning("Nenhum texto selecionado (ou seleção igual ao clipboard atual).")
        finally:
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

    async def toggle_tts(self) -> None:
        """Se está tocando áudio, para. Se não, faz speak_selection."""
        if self._player.is_playing():
            logger.info("Parando TTS em andamento.")
            self._player.stop()
            self.status = 'idle'
        else:
            await self.speak_selection()
