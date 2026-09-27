import asyncio
import logging
import sys
import threading
from dotenv import load_dotenv

from src.config import AppConfig
from src.engines import (
    EdgeTTSEngine,
    WhisperSTTEngine,
    PygameAudioPlayer,
    MicrophoneRecorder,
    ClipboardInjector
)
from src.app import VoiceDevApp, HotkeyManager, TrayIcon

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

async def async_main(app: VoiceDevApp):
    """
    Loop principal assíncrono para manter a thread ativa aguardando o fim do app.
    O TrayIcon será capaz de mandar um stop().
    """
    try:
        # Fica rodando indefinidamente (ou até o loop.stop() ser chamado no stop() do tray)
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass

def main():
    # 1. Carrega variáveis de ambiente
    load_dotenv()
    
    # 2. Configura logs
    configure_logging()
    logger = logging.getLogger("VoiceDev.Main")
    logger.info("Iniciando VoiceDev...")

    # 3. Carrega configurações
    try:
        config = AppConfig.from_env()
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        sys.exit(1)

    # Cria ou pega o loop de eventos
    # (Para Windows, o ProactorEventLoop é padrão no Python 3.8+)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 4. Instancia as engines
    logger.info("Carregando engines...")
    synthesizer = EdgeTTSEngine(
        voice=config.tts_voice,
        rate=config.tts_rate,
        pitch=config.tts_pitch
    )
    recognizer = WhisperSTTEngine(
        model_size=config.stt_model,
        device=config.stt_device,
        compute_type=config.stt_compute_type,
        language=config.stt_language
    )
    player = PygameAudioPlayer()
    recorder = MicrophoneRecorder()
    injector = ClipboardInjector()

    # 5. Instancia a Aplicação (App)
    app = VoiceDevApp(
        synthesizer=synthesizer,
        recognizer=recognizer,
        player=player,
        recorder=recorder,
        injector=injector
    )

    # 6. Instancia o HotkeyManager
    hotkeys = HotkeyManager()
    
    # Helpers para chamar as funções da UI no loop correto a partir da thread do keyboard
    def run_sync(func):
        loop.call_soon_threadsafe(func)

    def run_async(coro_func):
        asyncio.run_coroutine_threadsafe(coro_func(), loop)

    hotkeys.register(config.hotkey_stt_toggle, lambda: run_sync(app.toggle_recording))
    hotkeys.register(config.hotkey_tts_selection, lambda: run_async(app.toggle_tts))
    hotkeys.register(config.hotkey_tts_clipboard, lambda: run_async(app.speak_clipboard))

    # Inicia o listener de atalhos globais (pynput GlobalHotKeys)
    hotkeys.start()

    # 7. Instancia TrayIcon
    tray = TrayIcon(app)
    app.on_status_changed = tray.update_icon

    logger.info("Atalhos configurados:")
    logger.info(f" STT Toggle (Gravar): {config.hotkey_stt_toggle}")
    logger.info(f" TTS Seleção: {config.hotkey_tts_selection}")
    logger.info(f" TTS Clipboard: {config.hotkey_tts_clipboard}")

    # 8. Roda TrayIcon em uma thread separada para não bloquear o loop assíncrono do Python
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    logger.info("VoiceDev rodando. Use o ícone na bandeja ou atalhos para interagir.")
    
    # 9. Roda o Event Loop na thread principal
    try:
        loop.run_until_complete(async_main(app))
    except KeyboardInterrupt:
        logger.info("Encerrando via Ctrl+C...")
    finally:
        hotkeys.stop()
        tray.icon.stop()
        loop.close()
        logger.info("VoiceDev encerrado.")

if __name__ == "__main__":
    main()
