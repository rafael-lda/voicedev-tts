"""Teste do MarkdownCleaner."""
from src.engines.markdown_cleaner import MarkdownCleaner

c = MarkdownCleaner()

# Teste com texto tipico de agente IA
sample = """## Resultado da Analise

**O codigo esta correto!** Aqui esta o que foi feito:

1. Refatorei a classe `UserService` para usar *injecao de dependencia*
2. Adicionei testes unitarios

```python
class UserService:
    def __init__(self, repo: IUserRepo):
        self._repo = repo
```

### Proximos passos

- Implementar ~~cache~~ **validacao** de entrada
- Usar o [Guia de estilo](https://style.guide.com) como referencia

| Metrica | Antes | Depois |
|---------|-------|--------|
| Linhas  | 200   | 120    |
| Testes  | 0     | 15     |

> Nota: todas as mudancas sao retrocompativeis.
"""

result = c.clean(sample)
print("=== ORIGINAL ===")
print(sample[:200] + "...")
print()
print("=== LIMPO ===")
print(result)
print()
print(f"Original: {len(sample)} chars -> Limpo: {len(result)} chars")

