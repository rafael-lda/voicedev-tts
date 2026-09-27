import asyncio
import logging
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from .voice_dev_app import VoiceDevApp

logger = logging.getLogger(__name__)


def create_image(color: str) -> Image.Image:
    """
    Cria uma imagem circular simples para o ícone da bandeja.
    """
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=color)
    return image


class TrayIcon:
    """
    Ícone de bandeja (System Tray) para interagir com o VoiceDevApp.
    """

    def __init__(self, app: VoiceDevApp) -> None:
        self.app = app
        self._loop = asyncio.get_event_loop()
        
        # Cria imagens para os estados principal e gravação
        self.img_idle = create_image('green')
        self.img_recording = create_image('red')

        self.icon = pystray.Icon(
            "VoiceDev",
            icon=self.img_idle,
            title="VoiceDev - TTS & STT",
            menu=pystray.Menu(
                item('🎤 Gravar (Ctrl+Shift+F1)', lambda: self._run_safe(self.app.toggle_recording)),
                item('🔊 Ler Seleção (Ctrl+Shift+F2)', lambda: self._run_safe(self.app.toggle_tts)),
                item('📋 Ler Clipboard (Ctrl+Shift+F3)', lambda: self._run_safe(self.app.speak_clipboard)),
                pystray.Menu.SEPARATOR,
                item('❌ Sair', self.stop)
            )
        )

    def _run_safe(self, action) -> None:
        """
        Ajuda a despachar métodos síncronos e assíncronos no thread/loop correto.
        """
        if asyncio.iscoroutinefunction(action):
            asyncio.run_coroutine_threadsafe(action(), self._loop)
        else:
            self._loop.call_soon_threadsafe(action)

    def update_icon(self, status: str) -> None:
        """
        Atualiza o ícone (cor) e hover text dependendo do status do app.
        """
        if status == 'recording':
            self.icon.icon = self.img_recording
            self.icon.title = "VoiceDev - Gravando..."
        else:
            self.icon.icon = self.img_idle
            self.icon.title = f"VoiceDev - Status: {status}"

    def run(self) -> None:
        """
        Inicia o ícone da bandeja (método bloqueante).
        Deve ser chamado em thread separada ou run_detached se disponível.
        """
        logger.info("Iniciando ícone na bandeja...")
        self.icon.run()

    def stop(self, *args) -> None:
        """
        Para o ícone da bandeja.
        """
        logger.info("Parando ícone na bandeja e encerrando aplicação...")
        self.icon.stop()
        # Sinaliza ao loop asyncio para parar
        self._loop.call_soon_threadsafe(self._loop.stop)
