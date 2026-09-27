import io
import wave
import logging
import threading
import pyaudio
from src.contracts.audio_recorder import IAudioRecorder

logger = logging.getLogger(__name__)

class MicrophoneRecorder(IAudioRecorder):
    """
    Motor de gravação de áudio do microfone utilizando PyAudio.
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16

    def __init__(self):
        """
        Inicializa o MicrophoneRecorder.
        """
        self._audio = pyaudio.PyAudio()
        self._frames: list[bytes] = []
        self._recording: bool = False
        self._stream: pyaudio.Stream | None = None
        self._record_thread: threading.Thread | None = None
        logger.info("MicrophoneRecorder inicializado.")

    def start_recording(self) -> None:
        """
        Inicia a gravação de áudio a partir do microfone.
        """
        if self._recording:
            logger.warning("Gravação já está em andamento.")
            return

        self._frames.clear()
        self._recording = True

        try:
            self._stream = self._audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
            
            logger.info("Iniciando thread de captura do microfone...")
            self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
            self._record_thread.start()
        except Exception as e:
            self._recording = False
            logger.error(f"Falha ao iniciar o stream de gravação: {e}")
            raise

    def _record_loop(self) -> None:
        """
        Loop de captura de áudio executado em uma thread separada.
        """
        logger.debug("Loop de gravação ativado.")
        while self._recording and self._stream and self._stream.is_active():
            try:
                data = self._stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                self._frames.append(data)
            except Exception as e:
                logger.error(f"Erro durante a leitura do stream de gravação: {e}")
                break

    def stop_recording(self) -> bytes:
        """
        Para a gravação atual e retorna os dados de áudio no formato WAV.

        :return: Bytes do áudio no formato WAV.
        """
        if not self._recording:
            logger.warning("Nenhuma gravação em andamento para ser interrompida.")
            return b""

        logger.info("Parando a gravação de áudio...")
        self._recording = False
        
        if self._record_thread:
            self._record_thread.join()

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        wav_io = io.BytesIO()
        try:
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self._audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(b''.join(self._frames))
            
            wav_bytes = wav_io.getvalue()
            logger.info(f"Gravação concluída. Tamanho do áudio WAV: {len(wav_bytes)} bytes.")
            return wav_bytes
        except Exception as e:
            logger.error(f"Erro ao gerar o arquivo WAV em memória: {e}")
            raise
        finally:
            wav_io.close()

    def is_recording(self) -> bool:
        """
        Verifica se há uma gravação em andamento.

        :return: True se estiver gravando, False caso contrário.
        """
        return self._recording
    
    def __del__(self):
        """
        Garante a liberação dos recursos do PyAudio ao ser destruído.
        """
        if self._recording:
            self.stop_recording()
        if hasattr(self, '_audio') and self._audio:
            self._audio.terminate()
