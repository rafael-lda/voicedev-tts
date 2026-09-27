"""Módulo de configuração do aplicativo."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class AppConfig:
    """Classe de configuração do aplicativo que carrega variáveis de ambiente."""
    
    tts_voice: str
    tts_rate: str
    tts_pitch: str
    
    stt_model: str
    stt_device: str
    stt_compute_type: str
    stt_language: str
    
    hotkey_stt_toggle: str
    hotkey_tts_selection: str
    hotkey_tts_clipboard: str

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Carrega as configurações a partir do arquivo .env ou variáveis de ambiente."""
        load_dotenv()
        
        return cls(
            tts_voice=os.getenv("TTS_VOICE", "pt-BR-FranciscaNeural"),
            tts_rate=os.getenv("TTS_RATE", "+0%"),
            tts_pitch=os.getenv("TTS_PITCH", "+0Hz"),
            
            stt_model=os.getenv("STT_MODEL", "base"),
            stt_device=os.getenv("STT_DEVICE", "cpu"),
            stt_compute_type=os.getenv("STT_COMPUTE_TYPE", "int8"),
            stt_language=os.getenv("STT_LANGUAGE", "pt"),
            
            hotkey_stt_toggle=os.getenv("HOTKEY_STT_TOGGLE", "ctrl+shift+f1"),
            hotkey_tts_selection=os.getenv("HOTKEY_TTS_SELECTION", "ctrl+shift+f2"),
            hotkey_tts_clipboard=os.getenv("HOTKEY_TTS_CLIPBOARD", "ctrl+shift+f3"),
        )
