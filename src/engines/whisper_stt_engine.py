import io
import time
import logging
from typing import Optional

from faster_whisper import WhisperModel

from src.contracts.speech_recognizer import ISpeechRecognizer

logger = logging.getLogger(__name__)


class WhisperSTTEngine(ISpeechRecognizer):
    """
    Motor de reconhecimento de fala utilizando faster-whisper.
    Suporta lazy loading com retry para lidar com rate limiting do HuggingFace.
    """

    _MAX_RETRIES = 3
    _RETRY_DELAY_SECONDS = 5

    def __init__(
        self,
        model_size: str = 'base',
        device: str = 'cpu',
        compute_type: str = 'int8',
        language: str = 'pt'
    ) -> None:
        """
        Inicializa o WhisperSTTEngine com lazy loading do modelo.

        :param model_size: Tamanho do modelo Whisper ('tiny', 'base', 'small', 'medium').
        :param device: Dispositivo para inferência ('cpu' ou 'cuda').
        :param compute_type: Tipo de quantização ('int8', 'float16').
        :param language: Idioma padrão esperado no áudio ('pt' para português).
        """
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._language = language
        self._model: Optional[WhisperModel] = None

        logger.info(
            f"WhisperSTTEngine configurado: size={model_size}, "
            f"device={device}, compute_type={compute_type}, language={language}. "
            f"O modelo será carregado no primeiro uso."
        )

    def _ensure_model_loaded(self) -> None:
        """Carrega o modelo Whisper se ainda não estiver em memória, com retry."""
        if self._model is not None:
            return

        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Carregando WhisperModel (tentativa {attempt}/{self._MAX_RETRIES})..."
                )
                start_time = time.time()
                self._model = WhisperModel(
                    self._model_size,
                    device=self._device,
                    compute_type=self._compute_type
                )
                elapsed = time.time() - start_time
                logger.info(f"Modelo Whisper carregado em {elapsed:.2f} segundos.")
                return
            except Exception as e:
                logger.warning(f"Falha ao carregar modelo (tentativa {attempt}): {e}")
                if attempt < self._MAX_RETRIES:
                    logger.info(f"Aguardando {self._RETRY_DELAY_SECONDS}s antes de tentar novamente...")
                    time.sleep(self._RETRY_DELAY_SECONDS)
                else:
                    logger.error("Todas as tentativas de carregar o modelo falharam.")
                    raise

    def transcribe(self, audio_data: bytes) -> str:
        """
        Transcreve áudio no formato WAV para texto.

        :param audio_data: Dados do áudio em bytes (formato WAV).
        :return: Texto transcrito do áudio.
        """
        if not audio_data:
            logger.warning("Nenhum dado de áudio fornecido para transcrição.")
            return ""

        self._ensure_model_loaded()

        try:
            logger.info("Iniciando transcrição de áudio...")
            start_time = time.time()
            audio_io = io.BytesIO(audio_data)

            segments, _info = self._model.transcribe(
                audio_io,
                language=self._language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text_segments = [segment.text for segment in segments]
            transcription = " ".join(text_segments).strip()

            elapsed = time.time() - start_time
            logger.info(f"Transcrição concluída em {elapsed:.2f}s. Resultado: '{transcription}'")

            return transcription
        except Exception as e:
            logger.error(f"Erro durante a transcrição de áudio: {e}")
            raise
