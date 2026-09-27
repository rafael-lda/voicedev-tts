"""Teste MINIMO de hotkey Win32 - teclas numericas."""
import ctypes
import ctypes.wintypes
import threading
import time
import sys

print("Iniciando teste minimo...", flush=True)

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
VK_1 = 0x31  # tecla 1
VK_2 = 0x32  # tecla 2
VK_3 = 0x33  # tecla 3

user32 = ctypes.windll.user32
detectado = False


def hotkey_thread():
    global detectado
    mods = MOD_CONTROL | MOD_ALT | MOD_NOREPEAT

    ok1 = user32.RegisterHotKey(None, 1, mods, VK_1)
    ok2 = user32.RegisterHotKey(None, 2, mods, VK_2)
    ok3 = user32.RegisterHotKey(None, 3, mods, VK_3)

    print(f"  Ctrl+Alt+1: {'OK' if ok1 else 'FALHOU'}", flush=True)
    print(f"  Ctrl+Alt+2: {'OK' if ok2 else 'FALHOU'}", flush=True)
    print(f"  Ctrl+Alt+3: {'OK' if ok3 else 'FALHOU'}", flush=True)
    print("", flush=True)

    msg = ctypes.wintypes.MSG()
    while True:
        ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if ret <= 0:
            break
        if msg.message == WM_HOTKEY:
            detectado = True
            nomes = {1: "Ctrl+Alt+1 (STT)", 2: "Ctrl+Alt+2 (TTS)", 3: "Ctrl+Alt+3 (Clipboard)"}
            nome = nomes.get(msg.wParam, "???")
            print(f"\n!!! {nome} DETECTADO !!! FUNCIONOU !!!\n", flush=True)

    for i in range(1, 4):
        user32.UnregisterHotKey(None, i)


t = threading.Thread(target=hotkey_thread, daemon=True)
t.start()
time.sleep(0.3)

print("Pressione em qualquer janela:", flush=True)
print("  Ctrl+Alt+1  ->  STT Record", flush=True)
print("  Ctrl+Alt+2  ->  TTS Speak", flush=True)
print("  Ctrl+Alt+3  ->  TTS Clipboard", flush=True)
print("", flush=True)
print("Ctrl+C para sair.", flush=True)
print("", flush=True)

try:
    while True:
        time.sleep(5)
        if not detectado:
            print("... esperando ...", flush=True)
except KeyboardInterrupt:
    print("\nEncerrado.", flush=True)
