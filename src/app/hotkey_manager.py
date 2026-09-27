import logging
import threading
from typing import Callable
from pynput import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager:
    """
    Gerenciador de atalhos globais usando pynput.keyboard.Listener
    com rastreamento manual de estado — a abordagem mais confiável no Windows.
    """

    def __init__(self) -> None:
        self._hotkeys: dict[frozenset[str], Callable] = {}
        self._pressed_keys: set[str] = set()
        self._listener: keyboard.Listener | None = None
        self._lock = threading.Lock()

    def register(self, hotkey: str, callback: Callable) -> None:
        """
        Registra um atalho global.

        :param hotkey: Atalho no formato 'ctrl+alt+r'.
        :param callback: Função a ser chamada quando o atalho é pressionado.
        """
        key_set = frozenset(part.strip().lower() for part in hotkey.split('+'))
        self._hotkeys[key_set] = callback
        logger.info(f"Atalho registrado: {hotkey} -> {key_set}")

    def start(self) -> None:
        """Inicia o listener de teclado em background."""
        if not self._hotkeys:
            logger.warning("Nenhum atalho registrado.")
            return

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        logger.info(f"Listener iniciado com {len(self._hotkeys)} atalho(s).")

    def stop(self) -> None:
        """Para o listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Listener parado.")

    def _normalize_key(self, key) -> str:
        """Converte uma tecla pynput em string normalizada."""
        try:
            # Teclas especiais (ctrl, alt, shift, etc.)
            if hasattr(key, 'name'):
                name = key.name.lower()
                # Normaliza ctrl_l/ctrl_r → ctrl, alt_l/alt_r → alt, etc.
                if name.startswith('ctrl'):
                    return 'ctrl'
                if name.startswith('alt'):
                    return 'alt'
                if name.startswith('shift'):
                    return 'shift'
                return name
            # Teclas alfanuméricas
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            # Tecla virtual (vk code)
            if hasattr(key, 'vk') and key.vk:
                return f"vk_{key.vk}"
        except AttributeError:
            pass
        return str(key).lower()

    def _on_press(self, key) -> None:
        """Callback de tecla pressionada."""
        normalized = self._normalize_key(key)

        with self._lock:
            self._pressed_keys.add(normalized)
            current_keys = frozenset(self._pressed_keys)

        # Verifica se alguma combinação registrada está ativa
        for combo, callback in self._hotkeys.items():
            if combo.issubset(current_keys):
                logger.info(f"Atalho detectado: {combo}")
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Erro no callback do atalho {combo}: {e}")
                break

    def _on_release(self, key) -> None:
        """Callback de tecla liberada."""
        normalized = self._normalize_key(key)

        with self._lock:
            self._pressed_keys.discard(normalized)
