# VoiceDev

Pequeno painel flutuante para Windows que **lê em voz alta** (em português do Brasil) o texto que você copiou — pensado para ouvir respostas de agentes de IA (Claude Code, Antigravity etc.) sem precisar ler a tela.

O texto é "limpo" antes de ser falado: blocos de código, código inline, links, formatação Markdown e emojis são removidos, para que a voz leia só o que importa.

## O que você precisa

- Windows 10 ou 11
- Python 3.12 (ou próximo) instalado, com o comando `python` disponível
- Internet (a voz usa o serviço gratuito Microsoft Edge TTS)
- Caixa de som ou fone

## Instalação (uma vez só)

Abra um terminal (PowerShell) na pasta do projeto e rode:

```powershell
python -m venv venv
.\venv\Scripts\python -m pip install -r requirements.txt
```

> O `pyaudio` e o `faster-whisper` fazem parte de um recurso de ditado (STT) que está em pausa. Se o `pyaudio` falhar ao instalar, o TTS não depende dele: instale os demais pacotes (`edge-tts`, `pygame`, `keyboard`, `pyperclip`, `python-dotenv`) individualmente.

## Como usar

### 1. Abrir o programa

Dê dois cliques em **`iniciar.bat`**. Ele abre só o painel flutuante, sem janela preta de terminal. Se quiser, crie um atalho dele na Área de Trabalho.

### 2. Ler um texto

1. Selecione e **copie** (`Ctrl+C`) qualquer texto, em qualquer programa.
2. Clique em **Ler** no painel, ou use o atalho **`Alt+C`** (funciona mesmo com outra janela em foco).
3. A leitura começa em poucos segundos e vai tocando frase por frase.

### 3. Controles

| Ação | Botão | Atalho global |
|---|---|---|
| Ler o texto copiado / parar a leitura | **Ler** / **Parar** | `Alt+C` |
| Pausar / retomar | **Pausa** | `Alt+P` |

- O painel mostra o estado: *Pronto*, *Lendo…* etc.
- Arraste o painel com o mouse para onde quiser na tela.
- Para **fechar** o programa, clique no **X** do painel.

## Configuração (opcional)

Crie um arquivo `.env` na raiz do projeto para mudar a voz e a velocidade:

```env
TTS_VOICE=pt-BR-FranciscaNeural   # outra opção: pt-BR-AntonioNeural
TTS_RATE=+0%                      # ex.: +20% mais rápido, -10% mais lento
TTS_PITCH=+0Hz                    # tom da voz
```

Para ver todas as vozes disponíveis: `.\venv\Scripts\edge-tts --list-voices`

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Clico em abrir e nada aparece | O `iniciar.bat` esconde os erros. Rode `.\venv\Scripts\python -m src.voice_panel` no terminal para ver a mensagem. |
| Não sai som | Verifique a internet e o dispositivo de saída de áudio do Windows. |
| `Alt+C` não responde | Outro programa pode estar usando o mesmo atalho. Use os botões do painel. |
| Nada é lido | Confirme que copiou texto (`Ctrl+C`) antes de clicar em **Ler**. |

## Para quem quer entender o código

```
src/
├── contracts/    Interfaces (ISpeechSynthesizer, IAudioPlayer...) — o "o que"
├── engines/      Implementações: EdgeTTSEngine, PygameAudioPlayer, MarkdownCleaner
├── app/          Orquestração
├── config.py     Leitura do .env
└── voice_panel.py  Painel flutuante (tkinter) e atalhos globais
```

A interface depende só dos contratos; as engines são injetadas. Detalhes em [SPEC.md](SPEC.md), histórico de versões em [HISTORY.md](HISTORY.md), regras para agentes de IA em [CLAUDE.md](CLAUDE.md).

Testes manuais: `test_cleaner.py`, `test_tts.py`, `test_hotkeys.py`.

## Status

TTS funcionando. Ditado por voz (STT) com Whisper existe no código, mas está em pausa.
