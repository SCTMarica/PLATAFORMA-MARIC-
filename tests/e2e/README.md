# E2E — automação (Playwright)

Código da suite E2E. As **specs Gherkin** ficam em [`docs/e2e/`](../../docs/e2e/README.md).

Esta pasta usa Playwright com Python e uma stack Docker isolada.
As seeds pertencem ao Playwright (SQL via `psycopg`), não ao Django.

## Serviços

O profile `e2e` inicia somente quando solicitado:

- `db-e2e`: PostgreSQL sem porta exposta no host
- `web-e2e`: Django conectado exclusivamente ao `db-e2e`
- `playwright`: runner com Chromium e artefatos de falha

Assim, o reset do banco dos testes não altera o banco local de desenvolvimento.

## Execução

```bash
make e2e
```

Arquivo, teste ou ID:

```bash
make e2e-file FILE=tests/e2e/test_01_public_pages.py
make e2e-test TEST=tests/e2e/test_01_public_pages.py::test_e2e_01_001_visitor_opens_home
make e2e-id ID=e2e_01_001
```

Ver todos os alvos: `make help`.

## Conceitos do pytest (como a suite funciona)

### O que faz uma função ser teste?

**Não é o `@pytest.mark`.** É o nome:

- arquivo: `test_*.py` (configurado no `pytest.ini`)
- função: começa com `test_`

```python
def test_e2e_01_001_visitor_opens_home(...):  # pytest coleta e executa
def helper_login(...):                        # pytest ignora
```

### O que é `@pytest.mark`?

É só um **marcador/etiqueta**. Não cria parâmetros e não registra o teste.

| Mark | Papel |
| --- | --- |
| `@pytest.mark.e2e` | Grupo genérico “teste E2E” (`pytest -m e2e`) |
| `@pytest.mark.e2e_01_001` | ID do cenário, para filtrar (`make e2e-id ID=e2e_01_001`) |

Os nomes dos marks são nossos (registrados em `pytest.ini`) e espelham a spec:

```text
docs/e2e:  [E2E-01-001] + @e2e-01-001
teste:     @pytest.mark.e2e_01_001 + test_e2e_01_001_*
```

Se remover os marks, o teste ainda roda — só fica mais difícil filtrar por ID/grupo.

### O que são fixtures (os parâmetros)?

Fixtures são funções que **preparam dependências** e o pytest injeta pelo **nome igual**:

```python
# tests/e2e/conftest.py
@pytest.fixture
def db():
    ...
    yield conn

# tests/e2e/test_01_public_pages.py
def test_e2e_01_001_visitor_opens_home(page, app_url, db):
    #                         ↑       ↑       ↑
    #              mesmo nome das fixtures
```

| Parâmetro | Origem | O que entrega |
| --- | --- | --- |
| `page` | plugin `pytest-playwright` | página do browser |
| `app_url` | `conftest.py` | URL base (`E2E_BASE_URL`) |
| `db` | `conftest.py` | conexão Postgres + seed/reset |

O `conftest.py` é carregado automaticamente (não precisa importar).  
Se o parâmetro não tiver fixture com o mesmo nome → erro na coleta.

### Resumo rápido

| Coisa | Função |
| --- | --- |
| prefixo `test_` | “sou um teste, rode-me” |
| `@pytest.mark.*` | “me rotule / filtre assim” |
| parâmetros (`page`, `db`, …) | fixtures injetadas pelo nome |

## Estado do banco (por teste)

A fixture `db` em `conftest.py`:

1. abre uma conexão própria do Playwright
2. faz `TRUNCATE` das tabelas da aplicação
3. aplica o seed baseline
4. aplica seeds declaradas com `@seed(...)` no teste
5. faz `COMMIT` (obrigatório para o `web-e2e` enxergar os dados via HTTP)
6. executa o teste
7. limpa com `TRUNCATE` novamente

**Por que commit + truncate:** no PostgreSQL, outra conexão (a do Django) nunca lê
linhas não commitadas. Em E2E o browser bate no `web-e2e`, então o seed precisa
ser visível.

Declare seeds no cabeçalho do teste (não no corpo):

```python
from tests.e2e.helpers.seed import seed

@seed("home_news")
def test_e2e_01_003_...(page, app_url, db):
    page.goto(f"{app_url}/")
    ...

# várias seeds, ou a função direto:
@seed("home_banners", "home_news")
@seed(seed_home_banners)
```

Nomes registrados ficam em `tests/e2e/helpers/seed.py` (`SEED_REGISTRY`).
Ao criar uma seed nova, registre o nome lá (ou passe o callable).

## Language convention

- **Code** (functions, classes, variables, file names): English  
- **UI assertions, seed content, Gherkin/docs**: Portuguese  
- **Scenario IDs** (`E2E-01-001`): neutral

Example: `test_e2e_01_001_visitor_opens_home` asserts title/text in Portuguese.

## Evidência visual (vídeo + prints + trace)

Por padrão, `make e2e` / `make e2e-id` **só mostram resultado no terminal**
(`--video off --screenshot off --tracing off`). Nenhum arquivo é gerado.

Para gravar evidência, o comando precisa ser **explícito**:

```bash
make e2e-video              # suite completa com arquivos
make e2e-video-id ID=e2e_01_001
make e2e-demo ID=e2e_01_001 # evidência + slowmo
make e2e EVIDENCE=1         # qualquer alvo comum com evidência
```

Os arquivos vão para `test-results/`:

```text
test-results/
  2026-08-15_21-58-00/          ← horário desta execução (grupo/laço)
    E2E-01-001_visitante-acessa-a-pagina-inicial/
      video.mp4
      pagina-final.png
      trace.zip
    E2E-01-002_pagina-inicial-exibe-banners-ativos-do-carrossel/
      ...
```

O nome da pasta combina o ID com o título em português. Espaços, acentos e
símbolos são convertidos para um formato seguro, evitando problemas em scripts,
terminais, links e outros sistemas operacionais.

O arquivo `pagina-final.png` é um print da **última tela do aplicativo** (depois
dos asserts e destaques). O screenshot automático do Playwright fica desligado
nesse modo para não capturar cartão nenhum.

### Cartões de abertura e resultado

O vídeo final é montado em três partes e exportado como **MP4 (H.264)**:

```text
[ cartão de abertura ]  +  [ gravação WebM do Playwright ]  +  [ cartão de resultado ]
        1,5 s                  íntegra, sem cortes                      1,0 s
                                    ↓
                              video.mp4 (artefato final)
```

O Playwright só grava WebM de forma nativa. No fim da execução o `ffmpeg`
junta os cartões, converte para MP4 (mais leve e fácil de abrir no Windows /
Trello / WhatsApp) e remove o `.webm` bruto.

Abertura: ID + nome do cenário em português. Resultado, conforme o pytest:

- `APROVADO` em verde quando todas as verificações passaram;
- `REPROVADO` em vermelho quando o teste falhou;
- `REPROVADO` em vermelho também quando há falha conhecida (`xfail`);
- `NÃO EXECUTADO` em cinza quando o teste foi ignorado.

Esses cartões não precisam ser adicionados em cada teste. A fixture automática
`portuguese_title_card`, em `tests/e2e/conftest.py`, só entra quando `--video on`
foi pedido; o hook `pytest_runtest_makereport` captura o resultado real e
`tests/e2e/helpers/video.py` faz a junção + conversão para MP4. O `ffmpeg`
completo vem instalado na imagem em `tests/e2e/Dockerfile` (o que o Playwright
embute não tem `concat` / H.264). Se o `ffmpeg` não estiver disponível, o WebM
original é preservado como está.

Para testes novos, basta manter:

1. um marcador de ID, como `@pytest.mark.e2e_01_008`;
2. uma docstring em português, como
   `"""[E2E-01-008] Visitante acessa a página de contato"""`;
3. a fixture `page` na assinatura do teste.

Durante a coleta, a suite interrompe a execução se um teste novo não tiver
exatamente um ID ou se sua docstring não começar com o mesmo ID. Assim, nomes
genéricos em inglês não chegam aos vídeos por acidente.

| Artefato | Para quê |
| --- | --- |
| `video.mp4` | Vídeo completo do teste (anexar na doc / Trello) |
| `pagina-final.png` | Print da última tela do app (antes do cartão de resultado) |
| `trace.zip` | Passo a passo clicável (melhor que print solto) |

Fluxo típico para revisar/documentar:

```bash
make e2e-video-id ID=e2e_01_001
make e2e-results          # lista o que foi gerado
make e2e-open-video       # abre o vídeo
make e2e-show-trace       # abre o replay das etapas no navegador
```

O terminal só diz pass/fail. A confiança visual vem desses arquivos (quando
pedidos explicitamente).

### Vídeo “parado”? Por quê?

Muitos cenários só fazem `goto` + assert (sem cliques). O assert é quase instantâneo,
então o `.mp4` parece uma tela congelada.

Playwright ajuda com:

1. **`locator.highlight()`** — usamos via `spotlight()` antes de cada assert importante  
2. **`--slowmo`** — atrasa ações para o vídeo respirar  
3. **Trace Viewer** (`make e2e-show-trace`) — melhor que o vídeo para ver cada verificação

Para gerar vídeo de demo mais legível:

```bash
make e2e-demo ID=e2e_01_001
make e2e-open-video
# ou o passo a passo:
make e2e-show-trace
```
