# E2E — especificação

Esta pasta guarda o **inventário funcional** (Gherkin): o que deve ser testado.

A automação Playwright fica em [`tests/e2e/`](../../tests/e2e/) — como rodar, seeds e código.

## Separação (padrão do projeto)

| Pasta | Conteúdo |
| --- | --- |
| `docs/e2e/` | Specs Gherkin, prioridades, critérios de aceite |
| `tests/e2e/` | Playwright, fixtures, seeds SQL, Docker de teste |

## Cenários

| Arquivo | Escopo | Cenários |
| --- | --- | --- |
| [01_paginas_publicas.feature](01_paginas_publicas.feature) | Home, sobre, navegação, links, arquivos | 12 |
| [02_noticias_eventos_midia.feature](02_noticias_eventos_midia.feature) | Notícias, eventos, calendário, mídia | 15 |
| [03_inscricoes_contato.feature](03_inscricoes_contato.feature) | Inscrições e formulário de contato | 14 |
| [04_autenticacao.feature](04_autenticacao.feature) | Cadastro, login, reset, admin inicial | 19 |
| [05_portal_permissoes.feature](05_portal_permissoes.feature) | Portal do usuário e controle de acesso | 12 |
| [06_painel_admin.feature](06_painel_admin.feature) | Painel, branding, conteúdo, preview | 19 |
| [07_busca_i18n_acessibilidade.feature](07_busca_i18n_acessibilidade.feature) | Busca, idioma, tema e acessibilidade | 16 |

**Total:** 107 cenários (`@p0` 48 · `@p1` 48 · `@p2` 11)

## Status da automação

- **`@p0`:** 48/48 cenários com ID `@e2e-…` estão automatizados em `tests/e2e/`.
- **`@p1` / `@p2`:** ainda **não** automatizados (~59 cenários). Continuam como inventário / checklist manual até a próxima leva.
- Logout por botão “Sair” foi **removido** do inventário: a UI atual não expõe esse controle.

### Lacunas e cheiros conhecidos (não bloqueiam o `@p0`)

| Tema | Nota |
| --- | --- |
| Cobertura do produto | A suite `@p0` cobre o núcleo crítico (home, conteúdo público, inscrição/contato, auth, portal/perms, painel branding+conteúdo, busca/idioma). Não cobre o app inteiro: links/arquivos, menu mobile, paginação, conteúdo não publicado, e-mail de contato, VLibras, preview iframe, caminhos negativos, etc. |
| Drawer do painel | `tests/e2e/helpers/admin.py` abre seções do editor via `page.evaluate` (força o drawer no DOM). Se o clique/JS real quebrar, o teste pode continuar verde. Preferível: abrir pelo fluxo de UI real. |
| Spec vs UI (cores) | O Gherkin ainda fala em “modal” de cores; a UI é um **drawer**. Alinhar o texto do cenário quando for conveniente. |
| Duplicação admin | Pares 06-005/006, 007/008 e 009/010 refazem o cadastro inteiro no segundo cenário. Isolamento ok, mas caro; extrair helper/fixture de create reduziria ruído. |
| Sobreposição 04 × 05 | Login admin/supervisor (04) e acesso ao painel (05) exercitam caminhos muito parecidos. |
| Seletores | Alguns asserts usam CSS de layout (ex.: `.col-12` na busca) ou botão genérico; frágeis a refactor de markup. |
| Idioma | `E2E-07-004` já navega para `/sobre/`; `E2E-07-005` reforça persistência com pouco valor incremental. |

## Convenções

- `@p0` — fluxo crítico (bloqueia release; automatizar primeiro)
- `@p1` — funcional importante
- `@p2` — complementar / UX
- `@functional` — comportamento funcional (não visual puro)
- `Contexto` — pré-condições compartilhadas da Feature

### Identificadores (spec ↔ teste)

Cada cenário ganha um ID estável:

```text
E2E-<arquivo>-<seq>
```

Exemplo para `01_paginas_publicas.feature`:

| Spec | Tag Gherkin | Teste Playwright |
| --- | --- | --- |
| `[E2E-01-001] Visitante acessa a página inicial` | `@e2e-01-001` | `test_e2e_01_001_*` em `tests/e2e/test_01_public_pages.py` |

Regra: o número do arquivo Gherkin (`01`, `02`…) e o prefixo do arquivo de teste (`test_01_…`) são os mesmos.

**Language:** code identifiers in English (same as the Django app). UI assertions, seed content, and Gherkin stay in Portuguese.

## Estratégia de automação

1. Specs vivem aqui e são a fonte da verdade do aceite.
2. Implementação Playwright espelha os arquivos por domínio (`test_home.py`, depois auth, etc.).
3. Começar pelos `@p0`; `@p1`/`@p2` entram depois ou ficam como checklist manual.
4. Seeds e reset de banco são responsabilidade de `tests/e2e/`, não do Django.

## Como rodar a suite

Ver [`tests/e2e/README.md`](../../tests/e2e/README.md).
