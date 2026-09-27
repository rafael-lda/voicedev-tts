"""
VoiceDev - Painel flutuante TTS com limpeza de Markdown e streaming por sentencas.
"""
import asyncio
import re
import threading
import tkinter as tk
import logging
import sys
import pyperclip
from dotenv import load_dotenv

from src.config import AppConfig
from src.engines import EdgeTTSEngine, PygameAudioPlayer
from src.engines.markdown_cleaner import MarkdownCleaner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout,
)
logger = logging.getLogger("VoiceDev")


class SentenceSplitter:
    """Divide texto em sentencas para streaming TTS."""

    _SPLIT_PATTERN = re.compile(r'(?<=[.!?;:])\s+|(?<=\n)')

    def split(self, text: str) -> list[str]:
        """
        Divide texto em sentencas/trechos para fala incremental.

        :param text: Texto limpo (sem markdown).
        :return: Lista de trechos nao-vazios.
        """
        parts = self._SPLIT_PATTERN.split(text)
        result = [p.strip() for p in parts if p and p.strip()]

        # Se ficou muito fragmentado, agrupa trechos curtos
        merged = []
        buffer = ""
        for part in result:
            buffer = f"{buffer} {part}".strip() if buffer else part
            if len(buffer) >= 80:
                merged.append(buffer)
                buffer = ""
        if buffer:
            merged.append(buffer)

        return merged if merged else [text]


class VoicePanel:
    """Painel flutuante TTS com limpeza de Markdown e streaming."""

    _BG = "#1e1e2e"
    _FG = "#cdd6f4"
    _BTN_CLIP = "#89b4fa"
    _BTN_STOP = "#fab387"
    _STATUS_COLORS = {
        "idle": "#a6adc8",
        "synthesizing": "#89b4fa",
        "playing": "#a6e3a1",
    }

    def __init__(self) -> None:
        load_dotenv()
        self._config = AppConfig.from_env()

        # Engines
        self._tts = EdgeTTSEngine(
            voice=self._config.tts_voice,
            rate=self._config.tts_rate,
            pitch=self._config.tts_pitch,
        )
        self._player = PygameAudioPlayer()
        self._cleaner = MarkdownCleaner()
        self._splitter = SentenceSplitter()

        self._status = "idle"
        self._stop_requested = False

        # Asyncio loop em thread separada
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()

        # GUI
        self._root = tk.Tk()
        self._build_ui()

    def _build_ui(self) -> None:
        """Constroi a interface grafica."""
        root = self._root
        root.title("VoiceDev")
        root.configure(bg=self._BG)
        root.attributes("-topmost", True)
        root.resizable(False, False)

        # Posiciona no canto inferior direito
        root.update_idletasks()
        w, h = 280, 180
        x = root.winfo_screenwidth() - w - 20
        y = root.winfo_screenheight() - h - 80
        root.geometry(f"{w}x{h}+{x}+{y}")

        # Titulo
        tk.Label(
            root, text="VoiceDev TTS", font=("Segoe UI", 13, "bold"),
            bg=self._BG, fg=self._FG,
        ).pack(pady=(8, 2))

        # Status
        self._status_label = tk.Label(
            root, text="Pronto", font=("Segoe UI", 9),
            bg=self._BG, fg=self._STATUS_COLORS["idle"],
            wraplength=250,
        )
        self._status_label.pack(pady=(0, 8))

        # Frame de botoes
        btn_frame = tk.Frame(root, bg=self._BG)
        btn_frame.pack(fill=tk.X, padx=12)

        btn_style = dict(
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
            cursor="hand2", width=26, height=1,
            activebackground="#45475a",
        )

        # Botao Ler Clipboard
        self._btn_clip = tk.Button(
            btn_frame, text="Ler Clipboard", bg=self._BTN_CLIP,
            fg="#1e1e2e", command=self._on_clipboard, **btn_style,
        )
        self._btn_clip.pack(pady=4)

        # Botao Parar
        self._btn_stop = tk.Button(
            btn_frame, text="Parar", bg=self._BTN_STOP,
            fg="#1e1e2e", command=self._on_stop, **btn_style,
        )
        self._btn_stop.pack(pady=4)

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_status(self, text: str, color_key: str = "idle") -> None:
        """Atualiza o label de status na thread da GUI."""
        color = self._STATUS_COLORS.get(color_key, self._STATUS_COLORS["idle"])
        self._status = color_key
        self._root.after(0, lambda: self._status_label.config(text=text, fg=color))

    # ---- Acoes ----

    def _on_clipboard(self) -> None:
        """Le clipboard, limpa markdown, e fala com streaming."""
        raw_text = pyperclip.paste()
        if not raw_text or not raw_text.strip():
            self._set_status("Clipboard vazio")
            return

        # Limpa markdown
        clean_text = self._cleaner.clean(raw_text)
        if not clean_text:
            self._set_status("Texto vazio apos limpeza")
            return

        logger.info(f"Texto original: {len(raw_text)} chars -> limpo: {len(clean_text)} chars")
        self._stop_requested = False
        self._btn_clip.config(state=tk.DISABLED)
        asyncio.run_coroutine_threadsafe(self._speak_streaming(clean_text), self._loop)

    async def _speak_streaming(self, text: str) -> None:
        """Sintetiza e reproduz por sentencas — comeca a tocar mais rapido."""
        sentences = self._splitter.split(text)
        total = len(sentences)
        logger.info(f"Streaming TTS: {total} trecho(s)")

        for i, sentence in enumerate(sentences, 1):
            if self._stop_requested:
                logger.info("Streaming interrompido pelo usuario.")
                break

            self._set_status(f"Falando {i}/{total}...", "synthesizing")

            try:
                audio = await self._tts.synthesize(sentence)
                if self._stop_requested:
                    break

                self._set_status(f"Falando {i}/{total}...", "playing")
                self._player.play(audio)

                # Aguarda fim deste trecho
                while self._player.is_playing():
                    if self._stop_requested:
                        self._player.stop()
                        break
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Erro no trecho {i}: {e}")

        self._set_status("Pronto", "idle")
        self._root.after(0, lambda: self._btn_clip.config(state=tk.NORMAL))

    def _on_stop(self) -> None:
        """Para a reproducao."""
        self._stop_requested = True
        if self._player.is_playing():
            self._player.stop()
        self._set_status("Parado", "idle")
        self._btn_clip.config(state=tk.NORMAL)
        logger.info("Parado pelo usuario.")

    def _on_close(self) -> None:
        """Encerra a aplicacao."""
        self._stop_requested = True
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._root.destroy()

    def run(self) -> None:
        """Inicia o painel."""
        logger.info("VoiceDev TTS pronto!")
        self._root.mainloop()


if __name__ == "__main__":
    panel = VoicePanel()
    panel.run()
