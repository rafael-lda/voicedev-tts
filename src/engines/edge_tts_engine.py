import logging
import edge_tts
from src.contracts.speech_synthesizer import ISpeechSynthesizer

logger = logging.getLogger(__name__)

class EdgeTTSEngine(ISpeechSynthesizer):
    """
    Motor de síntese de voz utilizando Edge TTS.
    """

    def __init__(self, voice: str = 'pt-BR-FranciscaNeural', rate: str = '+0%', pitch: str = '+0Hz'):
        """
        Inicializa o EdgeTTSEngine.

        :param voice: Voz a ser utilizada. Padrão é 'pt-BR-FranciscaNeural'.
        :param rate: Taxa de velocidade da fala. Padrão é '+0%'.
        :param pitch: Tom da voz. Padrão é '+0Hz'.
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        logger.info(f"EdgeTTSEngine inicializado com voz={voice}, rate={rate}, pitch={pitch}")

    async def synthesize(self, text: str) -> bytes:
        """
        Sintetiza o texto em áudio MP3 utilizando edge-tts.

        :param text: O texto a ser sintetizado.
        :return: Bytes do áudio no formato MP3.
        :raises ValueError: Se o texto estiver vazio.
        :raises Exception: Em caso de falha de conexão ou erro do edge-tts.
        """
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido para síntese.")
            raise ValueError("O texto para síntese não pode ser vazio.")

        try:
            logger.debug(f"Iniciando síntese do texto: {text[:30]}...")
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            
            audio_bytes = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
                    
            logger.debug("Síntese concluída com sucesso.")
            return bytes(audio_bytes)
        except Exception as e:
            logger.error(f"Erro ao sintetizar o texto: {e}")
            raise
