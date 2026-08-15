# language: pt
Funcionalidade: Portal do usuário e permissões
  Como usuário autenticado
  Quero acessar apenas as áreas permitidas ao meu papel
  Para usar o portal com segurança

  @p0 @functional
  Cenário: Visitante não autenticado é redirecionado ao tentar abrir o portal
    Dado que o visitante não está autenticado
    Quando o visitante acessa "/portal/"
    Então o visitante deve ser redirecionado para "/login/"

  @p0 @functional
  Cenário: Cliente autenticado acessa o portal
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/portal/"
    Então a página do portal deve carregar com status 200

  @p1 @functional
  Cenário: Portal exibe o papel do usuário autenticado
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/portal/"
    Então o portal deve exibir o rótulo do papel "Cliente final"

  @p0 @functional
  Cenário: Cliente final não acessa o painel administrativo
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/painel-admin/"
    Então o acesso deve ser negado
    E o cliente não deve visualizar o painel administrativo

  @p0 @functional
  Cenário: Supervisor acessa o painel administrativo
    Dado que existe um supervisor autenticado
    Quando o supervisor acessa "/painel-admin/"
    Então a página do painel deve carregar com status 200

  @p0 @functional
  Cenário: Administrador master acessa o painel administrativo
    Dado que existe um administrador master autenticado
    Quando o administrador acessa "/painel-admin/"
    Então a página do painel deve carregar com status 200

  @p1 @functional
  Cenário: Usuário inativo não consegue autenticar
    Dado que existe um usuário inativo com credenciais conhecidas
    Quando o visitante tenta fazer login com essas credenciais
    Então o login deve falhar
    E a mensagem de conta inativa deve ser exibida

  @p1 @functional
  Cenário: Cliente não acessa cadastro de notícia no painel
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/painel-admin/noticias/nova/"
    Então o acesso deve ser negado

  @p1 @functional
  Cenário: Cliente não acessa cadastro de banner no painel
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/painel-admin/carrossel/novo/"
    Então o acesso deve ser negado

  @p1 @functional
  Cenário: Cliente não acessa criação de formulário de inscrição no painel
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/painel-admin/formularios/novo/"
    Então o acesso deve ser negado

  @p2 @functional
  Cenário: Após login o redirecionamento respeita parâmetro next seguro
    Dado que existe um cliente com credenciais válidas
    Quando o visitante acessa "/login/?next=/portal/"
    E faz login com sucesso
    Então o visitante deve ser redirecionado para "/portal/"

  @p2 @functional
  Cenário: Parâmetro next inseguro é ignorado no redirecionamento pós-login
    Dado que existe um cliente com credenciais válidas
    Quando o visitante acessa "/login/?next=https://site-malicioso.example"
    E faz login com sucesso
    Então o visitante deve ser redirecionado para a landing padrão do papel
    E não deve ser enviado para o domínio externo
