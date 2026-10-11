# Histórico do Projeto VoiceDev

## [Não lançado] - 2026-10-11
### Adicionado
- Painel redesenhado como barra fina de uma linha, sem título; botão de minimizar (recolhe para um mini botão); reafirmação periódica de `topmost` para não ir para trás da barra de tarefas.
- `README.md` didático com instalação, uso, configuração e solução de problemas.
- `iniciar.bat` na raiz do projeto: abre o painel via `pythonw.exe`, sem console.

## [v1.0.0] - 2026-09-27
### Adicionado
- Integração de Text-to-Speech (TTS) com motor `edge-tts`.
- Reprodução de áudio assíncrona utilizando `pygame`.
- Limpeza rigorosa de Markdown com `MarkdownCleaner` (suporte a remoção de formatações, links, blocos de código e emojis) para síntese natural da fala.
- Otimização de latência: Divisão de texto em sentenças lógicas (`SentenceSplitter`) para envio via streaming/chunks.
- Interface gráfica (GUI) minimalista, sem bordas (`borderless`), arrastável e com botões compactos.
- Atalhos globais com `keyboard`: `Alt+C` (Ler/Parar) e `Alt+P` (Pausar/Retomar), para operar o TTS mesmo fora da janela.
- Controle avançado de player: Implementação de pausa/retomada no `pygame` e nos contratos (`IAudioPlayer`).
- Script `.bat` de inicialização rodando de forma silenciosa via `pythonw.exe` para ocultar o terminal preto.
- Arquitetura limpa fortemente baseada em interfaces (`src/contracts`) e injeção de dependência.

### Adiado (Em Espera)
- Funcionalidade STT (Speech-to-Text) com `faster-whisper`. A infraestrutura básica (`WhisperSTTEngine` e `ClipboardInjector`) existe, mas o recurso está em pausa para focar na estabilidade do TTS via GUI.
- Atalhos globais (`hotkeys` via `pynput` / API do Windows), desativados em prol da interface gráfica flutuante.
