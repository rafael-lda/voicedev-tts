"""Script de teste funcional rápido do TTS."""
import asyncio
from src.engines.edge_tts_engine import EdgeTTSEngine
from src.engines.pygame_audio_player import PygameAudioPlayer


async def test_tts():
    """Testa a síntese e reprodução de áudio."""
    engine = EdgeTTSEngine()
    print("Sintetizando áudio...")
    audio = await engine.synthesize("Olá! VoiceDev funcionando com sucesso.")
    print(f"Áudio gerado: {len(audio)} bytes")

    player = PygameAudioPlayer()
    print("Reproduzindo áudio...")
    player.play(audio)

    # Aguarda a reprodução terminar
    import time
    while player.is_playing():
        time.sleep(0.2)

    print("Teste concluído com sucesso!")


if __name__ == "__main__":
    asyncio.run(test_tts())

