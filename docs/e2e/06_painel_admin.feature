# language: pt
Funcionalidade: Painel administrativo
  Como administrador ou supervisor
  Quero gerenciar conteúdo e aparência do site
  Para manter o portal institucional atualizado

  Contexto:
    Dado que existe um administrador master autenticado
    E que o site possui configurações institucionais básicas

  # IDs: E2E-06-<seq>  →  espelhado em tests/e2e/test_06_admin_*.py

  @p0 @functional @e2e-06-001
  Cenário: [E2E-06-001] Admin acessa o painel administrativo
    Quando o administrador acessa "/painel-admin/"
    Então a página do painel deve carregar com status 200
    E o formulário de configurações do site deve estar visível

  @p0 @functional @e2e-06-002
  Cenário: [E2E-06-002] Admin atualiza configurações gerais do site
    Quando o administrador altera o nome do site e o título do hero
    E salva as configurações em "/painel-admin/"
    Então deve ver a mensagem "Conteudo do site atualizado com sucesso."
    E as novas configurações devem permanecer salvas ao recarregar o painel

  @p0 @functional @e2e-06-003
  Cenário: [E2E-06-003] Alterações de branding aparecem na página pública
    Dado que o administrador alterou o nome do site para "Portal Maricá"
    Quando o visitante acessa "/"
    Então o cabeçalho deve exibir "Portal Maricá"

  @p0 @functional @e2e-06-004
  Cenário: [E2E-06-004] Admin atualiza cores do sistema pelo modal dedicado
    Quando o administrador abre o modal "Cores do sistema"
    E altera as cores primária, secundária e de destaque
    E salva as alterações
    Então as novas cores devem ser persistidas nas configurações do site

  @p1 @functional
  Cenário: Painel exibe preview visual da home embutido
    Quando o administrador acessa "/painel-admin/"
    Então deve existir um iframe de preview apontando para a home com "admin_preview=1"

  @p1 @functional
  Cenário: Preview da home em modo admin_preview mostra controles de edição
    Quando o administrador acessa "/?admin_preview=1"
    Então os controles de edição do preview devem estar visíveis

  @p1 @functional
  Cenário: Home pública não exibe controles de edição do preview
    Dado que o visitante não está em modo admin_preview
    Quando o visitante acessa "/"
    Então os controles de edição do preview não devem aparecer

  @p0 @functional @e2e-06-005
  Cenário: [E2E-06-005] Admin cadastra uma nova notícia
    Quando o administrador acessa "/painel-admin/noticias/nova/"
    E preenche título, resumo, conteúdo e publica a notícia
    E salva o formulário
    Então deve ver a mensagem "Noticia cadastrada com sucesso."
    E deve ser redirecionado para "/painel-admin/"

  @p0 @functional @e2e-06-006
  Cenário: [E2E-06-006] Notícia cadastrada aparece na listagem pública quando publicada
    Dado que o administrador cadastrou a notícia publicada "Nova edição"
    Quando o visitante acessa "/noticias/"
    Então a notícia "Nova edição" deve aparecer na lista

  @p1 @functional
  Cenário: Admin cadastra notícia em destaque e ela aparece na home
    Quando o administrador cadastra uma notícia publicada marcada como destaque
    E o visitante acessa "/"
    Então a notícia em destaque deve aparecer na home

  @p0 @functional @e2e-06-007
  Cenário: [E2E-06-007] Admin cadastra imagem no carrossel
    Quando o administrador acessa "/painel-admin/carrossel/novo/"
    E preenche título, URL da imagem e ordem
    E salva o formulário
    Então deve ver a mensagem "Imagem do carrossel cadastrada com sucesso."
    E deve ser redirecionado para "/painel-admin/"

  @p0 @functional @e2e-06-008
  Cenário: [E2E-06-008] Banner cadastrado aparece na home quando ativo
    Dado que o administrador cadastrou um banner ativo "Campanha verão"
    Quando o visitante acessa "/"
    Então o banner "Campanha verão" deve aparecer no carrossel

  @p0 @functional @e2e-06-009
  Cenário: [E2E-06-009] Admin cria formulário de inscrição
    Quando o administrador acessa "/painel-admin/formularios/novo/"
    E preenche título, descrição e schema de campos
    E salva o formulário
    Então deve ver a mensagem "Formulario de inscricao criado com sucesso."
    E deve ser redirecionado para "/painel-admin/"

  @p0 @functional @e2e-06-010
  Cenário: [E2E-06-010] Formulário criado aparece na listagem pública de inscrições quando ativo
    Dado que o administrador criou o formulário ativo "Inscrição 2026"
    Quando o visitante acessa "/inscreva-se/"
    Então o formulário "Inscrição 2026" deve aparecer na lista

  @p1 @functional
  Cenário: Painel exibe contagem de mensagens de contato novas
    Dado que existem mensagens de contato com status "nova"
    Quando o administrador acessa "/painel-admin/"
    Então a contagem de mensagens novas deve ser exibida no painel

  @p1 @functional
  Cenário: Admin consegue salvar destino de e-mail do formulário de contato
    Quando o administrador define "contact_email_destination" como "ouvidoria@teste.com"
    E salva as configurações do site
    Então o valor "ouvidoria@teste.com" deve permanecer salvo

  @p2 @functional
  Cenário: Cadastro admin de notícia com dados inválidos não salva
    Quando o administrador tenta salvar uma notícia sem título obrigatório
    Então a notícia não deve ser criada
    E o formulário deve exibir erro de validação

  @p2 @functional
  Cenário: Cadastro admin de banner com dados inválidos não salva
    Quando o administrador tenta salvar um banner sem os campos obrigatórios
    Então o banner não deve ser criado
    E o formulário deve exibir erro de validação

  @p2 @functional
  Cenário: Cadastro admin de formulário com dados inválidos não salva
    Quando o administrador tenta salvar um formulário de inscrição sem título
    Então o formulário de inscrição não deve ser criado
    E a tela deve exibir erro de validação
