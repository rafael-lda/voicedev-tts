"""
VoiceDev - Painel flutuante TTS minimalista com atalhos globais.
"""
import asyncio
import re
import threading
import tkinter as tk
import logging
import sys
import pyperclip
import keyboard
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
        parts = self._SPLIT_PATTERN.split(text)
        result = [p.strip() for p in parts if p and p.strip()]
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
    """Painel flutuante TTS minimalista e dragable."""

    _BG = "#1e1e2e"
    _FG = "#cdd6f4"
    _BTN_CLIP = "#89b4fa"
    _BTN_STOP = "#f38ba8"
    _BTN_PAUSE = "#f9e2af"
    _STATUS_COLORS = {
        "idle": "#a6adc8",
        "synthesizing": "#89b4fa",
        "playing": "#a6e3a1",
        "paused": "#f9e2af"
    }

    def __init__(self) -> None:
        load_dotenv()
        self._config = AppConfig.from_env()

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
        self._paused = False

        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()

        self._root = tk.Tk()
        self._build_ui()
        self._setup_hotkeys()

    def _build_ui(self) -> None:
        root = self._root
        root.title("VoiceDev")
        root.configure(bg=self._BG)
        root.attributes("-topmost", True)
        root.overrideredirect(True) # Remove as bordas nativas da janela
        
        w, h = 230, 65
        x = root.winfo_screenwidth() - w - 20
        y = root.winfo_screenheight() - h - 60
        root.geometry(f"{w}x{h}+{x}+{y}")

        main_frame = tk.Frame(root, bg=self._BG, highlightbackground="#45475a", highlightthickness=1)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Botão de fechar (x) minúsculo no canto
        close_btn = tk.Label(main_frame, text="✕", bg=self._BG, fg="#f38ba8", font=("Segoe UI", 9, "bold"), cursor="hand2")
        close_btn.place(x=210, y=2)
        close_btn.bind("<Button-1>", lambda e: self._on_close())

        # Area para arrastar (Drag and Drop)
        drag_area = tk.Label(main_frame, text="  VoiceDev (Alt+C para ler)  ", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 8), cursor="fleur")
        drag_area.place(x=1, y=1, width=205, height=18)
        
        def start_move(event):
            self.x = event.x
            self.y = event.y
        def stop_move(event):
            self.x = None
            self.y = None
        def do_move(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            new_x = root.winfo_x() + deltax
            new_y = root.winfo_y() + deltay
            root.geometry(f"+{new_x}+{new_y}")

        drag_area.bind("<ButtonPress-1>", start_move)
        drag_area.bind("<ButtonRelease-1>", stop_move)
        drag_area.bind("<B1-Motion>", do_move)

        # Status
        self._status_label = tk.Label(
            main_frame, text="Pronto", font=("Segoe UI", 8),
            bg=self._BG, fg=self._STATUS_COLORS["idle"],
            wraplength=200
        )
        self._status_label.place(x=10, y=20)

        # Botões
        btn_frame = tk.Frame(main_frame, bg=self._BG)
        btn_frame.place(x=10, y=40)

        btn_style = dict(font=("Segoe UI", 8, "bold"), relief=tk.FLAT, cursor="hand2", width=7, height=1)

        self._btn_clip = tk.Button(btn_frame, text="▶ Ler", bg=self._BTN_CLIP, fg="#1e1e2e", command=self._on_clipboard, **btn_style)
        self._btn_clip.pack(side=tk.LEFT, padx=(0, 5))

        self._btn_pause = tk.Button(btn_frame, text="⏸ Pausa", bg=self._BTN_PAUSE, fg="#1e1e2e", command=self._toggle_pause, **btn_style)
        self._btn_pause.pack(side=tk.LEFT, padx=5)

        self._btn_stop = tk.Button(btn_frame, text="⏹ Parar", bg=self._BTN_STOP, fg="#1e1e2e", command=self._on_stop, **btn_style)
        self._btn_stop.pack(side=tk.LEFT, padx=5)

    def _setup_hotkeys(self):
        try:
            keyboard.add_hotkey('alt+c', lambda: self._root.after(0, self._toggle_read))
            keyboard.add_hotkey('alt+p', lambda: self._root.after(0, self._toggle_pause))
            logger.info("Atalhos globais ativados: Alt+C (Ler/Parar), Alt+P (Pausar/Retomar)")
        except Exception as e:
            logger.error(f"Erro ao registrar atalhos: {e}")

    def _set_status(self, text: str, color_key: str = "idle") -> None:
        color = self._STATUS_COLORS.get(color_key, self._STATUS_COLORS["idle"])
        self._status = color_key
        self._root.after(0, lambda: self._status_label.config(text=text, fg=color))

    def _toggle_read(self):
        """Inicia a leitura ou para se já estiver lendo."""
        if self._player.is_playing() or self._status in ["playing", "synthesizing", "paused"]:
            self._on_stop()
        else:
            self._on_clipboard()

    def _toggle_pause(self):
        """Pausa ou retoma a leitura."""
        if self._status == "idle" and not self._player.is_playing():
            return
            
        if self._paused:
            self._player.unpause()
            self._paused = False
            self._set_status("Tocando...", "playing")
        else:
            self._player.pause()
            self._paused = True
            self._set_status("Pausado (Alt+P para retomar)", "paused")

    def _on_clipboard(self) -> None:
        raw_text = pyperclip.paste()
        if not raw_text or not raw_text.strip():
            self._set_status("Clipboard vazio")
            return

        clean_text = self._cleaner.clean(raw_text)
        if not clean_text:
            self._set_status("Texto vazio apos limpeza")
            return

        self._stop_requested = False
        self._paused = False
        self._btn_clip.config(state=tk.DISABLED)
        asyncio.run_coroutine_threadsafe(self._speak_streaming(clean_text), self._loop)

    async def _speak_streaming(self, text: str) -> None:
        sentences = self._splitter.split(text)
        total = len(sentences)

        for i, sentence in enumerate(sentences, 1):
            if self._stop_requested:
                break

            self._set_status(f"Falando {i}/{total}...", "synthesizing")
            try:
                audio = await self._tts.synthesize(sentence)
                if self._stop_requested:
                    break

                self._set_status(f"Falando {i}/{total}...", "playing")
                self._player.play(audio)

                while self._player.is_playing() and not self._stop_requested:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Erro no trecho {i}: {e}")

        if not self._stop_requested:
            self._set_status("Pronto", "idle")
            self._paused = False
        
        self._root.after(0, lambda: self._btn_clip.config(state=tk.NORMAL))

    def _on_stop(self) -> None:
        self._stop_requested = True
        self._paused = False
        if self._player.is_playing():
            self._player.stop()
        self._set_status("Parado", "idle")
        self._btn_clip.config(state=tk.NORMAL)

    def _on_close(self) -> None:
        self._stop_requested = True
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._root.destroy()
        sys.exit(0)

    def run(self) -> None:
        self._root.mainloop()

if __name__ == "__main__":
    panel = VoicePanel()
    panel.run()
