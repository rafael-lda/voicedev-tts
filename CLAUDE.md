# Regras do Projeto VoiceDev

Este projeto utiliza ferramentas de desenvolvimento orientadas por Agentes de IA. Ao interagir com este repositório, agentes devem seguir estritamente as regras abaixo:

## 1. Regra de Conformidade Documental (OBRIGATÓRIO)
**TODA e QUALQUER alteração no código DEVE ser acompanhada pela atualização correspondente na documentação do projeto.**
- Ao adicionar, modificar ou remover uma funcionalidade ou fluxo de dados, você **DEVE** obrigatoriamente editar o `SPEC.md` para refletir o novo design/arquitetura/fluxo.
- Você **DEVE** registrar o que foi feito no arquivo `HISTORY.md`.
- O código só é considerado pronto quando a documentação (Spec e Histórico) estiverem 100% sincronizadas e refletirem com fidelidade as capacidades atuais do código.

## 2. Princípios de Engenharia de Software
- **Orientação a Objetos Forte**: O projeto baseia-se em encapsular responsabilidades e estado. Funções soltas ou scripts procedurais puros são inaceitáveis.
- **Inversão de Dependência (SOLID)**: Todo módulo de alto nível (App, UI) depende apenas dos contratos definidos em `src/contracts`. Nenhuma UI ou orquestrador pode referenciar bibliotecas de baixo nível de engines diretamente se não por injeção.
- **Isolamento**: Cada `Engine` faz apenas um papel de comunicação com a biblioteca externa.

## 3. Idioma Padrão
- O idioma de commits, respostas, arquivos markdown (`HISTORY.md`, `SPEC.md`) e nomes semânticos locais deve priorizar **Português do Brasil (pt-BR)**.
