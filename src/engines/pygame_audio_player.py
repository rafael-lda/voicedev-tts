import io
import logging
import pygame
from src.contracts.audio_player import IAudioPlayer

logger = logging.getLogger(__name__)

class PygameAudioPlayer(IAudioPlayer):
    """
    Motor de reprodução de áudio utilizando pygame.
    """

    def __init__(self):
        """
        Inicializa o PygameAudioPlayer e o pygame.mixer.
        """
        try:
            pygame.mixer.init(frequency=24000)
            logger.info("pygame.mixer inicializado com sucesso em 24000 Hz.")
        except Exception as e:
            logger.error(f"Falha ao inicializar pygame.mixer: {e}")
            raise

    def play(self, audio_bytes: bytes) -> None:
        """
        Reproduz os bytes de áudio.

        :param audio_bytes: Bytes do áudio no formato suportado (MP3).
        """
        if not audio_bytes:
            logger.warning("Nenhum byte de áudio fornecido para reprodução.")
            return

        try:
            logger.debug("Carregando e reproduzindo áudio...")
            audio_io = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_io)
            pygame.mixer.music.play()
        except Exception as e:
            logger.error(f"Erro ao tentar reproduzir o áudio: {e}")
            raise

    def stop(self) -> None:
        """
        Para a reprodução de áudio imediatamente.
        """
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            logger.debug("Reprodução de áudio parada.")

    def is_playing(self) -> bool:
        """
        Verifica se há áudio sendo reproduzido.

        :return: True se estiver reproduzindo, False caso contrário.
        """
        if pygame.mixer.get_init():
            return pygame.mixer.music.get_busy()
        return False
