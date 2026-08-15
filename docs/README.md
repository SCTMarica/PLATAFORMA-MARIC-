# Documentação — Plataforma Maric

## Testes E2E (Gherkin)

Inventário funcional dos cenários de ponta a ponta, com passos `Dado` / `Quando` / `Então`.

**Totais atuais**

| Tipo | Quantidade |
| --- | --- |
| Cenários E2E (Gherkin) | **110** |
| Prioridade `@p0` | 51 |
| Prioridade `@p1` | 48 |
| Prioridade `@p2` | 11 |
| Testes unitários/Django existentes (`core/tests.py`) | 24 |

| Arquivo | Escopo | Cenários |
| --- | --- | --- |
| [e2e/01_paginas_publicas.feature](e2e/01_paginas_publicas.feature) | Home, sobre, navegação, links, arquivos | 13 |
| [e2e/02_noticias_eventos_midia.feature](e2e/02_noticias_eventos_midia.feature) | Notícias, eventos, calendário, mídia | 15 |
| [e2e/03_inscricoes_contato.feature](e2e/03_inscricoes_contato.feature) | Inscrições e formulário de contato | 14 |
| [e2e/04_autenticacao.feature](e2e/04_autenticacao.feature) | Cadastro, login, logout, reset, admin inicial | 21 |
| [e2e/05_portal_permissoes.feature](e2e/05_portal_permissoes.feature) | Portal do usuário e controle de acesso | 12 |
| [e2e/06_painel_admin.feature](e2e/06_painel_admin.feature) | Painel, branding, conteúdo, preview | 19 |
| [e2e/07_busca_i18n_acessibilidade.feature](e2e/07_busca_i18n_acessibilidade.feature) | Busca, idioma, tema e acessibilidade | 16 |

### Convenções

- `@p0` — fluxo crítico (bloqueia release)
- `@p1` — funcional importante
- `@p2` — complementar / UX
- `@functional` — comportamento funcional (não visual puro)
- `Contexto` — pré-condições compartilhadas da Feature
- Cada cenário descreve ação + resultado esperado (pronto para virar automação)

### Próximos passos

1. Revisar passos com o time e ajustar ambiguidades
2. Implementar os cenários `@p0`, começando pela home e autenticação
3. Expandir seeds Playwright em `tests/e2e/db/seeds/` (independentes do Django)
4. Executar a suite com a [documentação de E2E](../tests/e2e/README.md)
