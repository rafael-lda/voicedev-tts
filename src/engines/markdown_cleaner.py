"""Limpeza de texto Markdown para sintese de voz natural."""
import re
import logging

logger = logging.getLogger(__name__)


class MarkdownCleaner:
    """
    Remove formatacao Markdown e elementos visuais do texto
    antes de enviar ao motor TTS, produzindo fala mais natural.
    """

    # Padroes compilados para performance
    _PATTERNS: list[tuple[re.Pattern, str]] = [
        # Blocos de codigo (``` ... ```) — remove inteiro
        (re.compile(r'```[\s\S]*?```', re.MULTILINE), ''),
        # Codigo inline (`codigo`) — mantem so o conteudo
        (re.compile(r'`([^`]+)`'), r'\1'),
        # Links markdown [texto](url) — mantem so o texto
        (re.compile(r'\[([^\]]+)\]\([^)]+\)'), r'\1'),
        # Imagens ![alt](url) — remove
        (re.compile(r'!\[[^\]]*\]\([^)]+\)'), ''),
        # Headers (# ## ### etc) — remove os hashes
        (re.compile(r'^#{1,6}\s+', re.MULTILINE), ''),
        # Negrito **texto** ou __texto__
        (re.compile(r'\*\*([^*]+)\*\*'), r'\1'),
        (re.compile(r'__([^_]+)__'), r'\1'),
        # Italico *texto* ou _texto_
        (re.compile(r'\*([^*]+)\*'), r'\1'),
        (re.compile(r'(?<!\w)_([^_]+)_(?!\w)'), r'\1'),
        # Strikethrough ~~texto~~
        (re.compile(r'~~([^~]+)~~'), r'\1'),
        # Listas com marcador (- item, * item, + item)
        (re.compile(r'^\s*[-*+]\s+', re.MULTILINE), ''),
        # Listas numeradas (1. item)
        (re.compile(r'^\s*\d+\.\s+', re.MULTILINE), ''),
        # Blockquotes (> texto)
        (re.compile(r'^\s*>\s*', re.MULTILINE), ''),
        # Linhas horizontais (--- ou ***)
        (re.compile(r'^[-*_]{3,}\s*$', re.MULTILINE), ''),
        # Tabelas markdown (| col | col |) — remove pipes
        (re.compile(r'\|'), ' '),
        # Linhas de separacao de tabela (|---|---|)
        (re.compile(r'^[\s|:-]+$', re.MULTILINE), ''),
        # HTML tags simples
        (re.compile(r'<[^>]+>'), ''),
    ]

    # Emojis comuns em interfaces de agentes IA
    _EMOJI_PATTERN = re.compile(
        r'[\U0001F300-\U0001F9FF'   # Emoticons e simbolos
        r'\U00002600-\U000027BF'    # Simbolos diversos
        r'\U0000FE00-\U0000FE0F'    # Variacao de estilo
        r'\U0000200D'               # Zero-width joiner
        r'\U00002702-\U000027B0'    # Dingbats
        r'\U0001FA00-\U0001FA6F'    # Novos simbolos
        r'\U0001FA70-\U0001FAFF'    # Mais simbolos
        r']+',
        flags=re.UNICODE
    )

    def clean(self, text: str) -> str:
        """
        Remove formatacao Markdown e emojis do texto.

        :param text: Texto bruto com possivel formatacao Markdown.
        :return: Texto limpo pronto para sintese de voz.
        """
        if not text:
            return ""

        result = text

        # Aplica todos os padroes de limpeza
        for pattern, replacement in self._PATTERNS:
            result = pattern.sub(replacement, result)

        # Remove emojis
        result = self._EMOJI_PATTERN.sub('', result)

        # Limpa espacos extras e linhas vazias
        result = re.sub(r'[ \t]+', ' ', result)          # Espacos multiplos
        result = re.sub(r'\n\s*\n+', '\n', result)       # Linhas vazias
        result = result.strip()

        if result != text:
            logger.debug(f"Texto limpo: {len(text)} -> {len(result)} chars")

        return result

