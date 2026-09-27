# Especificação do Projeto VoiceDev (Spec)

## 1. Visão Geral
O **VoiceDev** é uma ferramenta complementar ao VS Code voltada para auxiliar desenvolvedores que utilizam Agentes de IA (como Antigravity ou Claude Code). O sistema fornece o Text-to-Speech (TTS) otimizado para código e Markdown, lendo respostas de IA em voz natural.

**Status Operacional**: TTS funcionando perfeitamente via painel GUI `tkinter`.

## 2. Padrões de Arquitetura
O sistema é projetado seguindo princípios SOLID, utilizando Alta Coesão e Baixo Acoplamento.

### 2.1 Camada de Contratos (Interfaces / `src/contracts`)
Define a API de comunicação do sistema usando classes abstratas (`ABC`):
- `ISpeechSynthesizer`: Contrato para conversão de texto em áudio.
- `IAudioPlayer`: Contrato para reprodução, interrupção, pausa e retomada de mídia.
- `ISpeechRecognizer`: Contrato para conversão de áudio em texto (STT).
- `IAudioRecorder`: Contrato para captura de microfone.
- `ITextInjector`: Contrato para colar texto no sistema do usuário.

### 2.2 Camada de Engines (Concretas / `src/engines`)
As implementações dos contratos acima:
- `EdgeTTSEngine`: Usa `edge-tts` (motor Microsoft Neural gratuito).
- `PygameAudioPlayer`: Usa o mixer do `pygame` (24000 Hz) para stream em RAM, suportando métodos `.pause()` e `.unpause()`.
- `MarkdownCleaner`: Componente vital que sanifica textos LLM descartando código inline, blocos de código e emojis antes de passar para o Sintetizador.
- *Adiados*: `WhisperSTTEngine` (faster-whisper), `MicrophoneRecorder` (pyaudio), `ClipboardInjector`.

### 2.3 Camada de Apresentação (UI / `src/voice_panel.py`)
A interface gráfica é responsável por orquestrar a limpeza e a execução do áudio.
- **Minimalista e Borderless**: A janela usa `overrideredirect(True)` para se comportar como um pequeno widget (semelhante ao Windows Dictation), que pode ser arrastado pelo usuário.
- **Atalhos Globais (`keyboard`)**: `Alt+C` para Ler/Parar e `Alt+P` para Pausar/Retomar.
- `SentenceSplitter`: Para evitar o lag do TTS em blocos gigantes de texto, divide por pontuação para tocar sequencialmente.
- O painel opera de forma assíncrona usando `asyncio` atrelado a uma thread daemon rodando as chamadas do motor.

## 3. Fluxo Principal de Uso
1. O usuário copia um texto do chat da IA para o clipboard.
2. Clica no botão "Ler Clipboard" da interface VoiceDev.
3. A string passa pelo `MarkdownCleaner`.
4. O `SentenceSplitter` fatia a string limpa em uma lista de sentenças curtas.
5. Em loop: Uma sentença é sintetizada no `EdgeTTSEngine` e imediatamente repassada ao `PygameAudioPlayer`. Caso o usuário clique em "Parar", o loop quebra e a flag aborta a próxima síntese.
