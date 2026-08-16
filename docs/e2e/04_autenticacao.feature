# language: pt
Funcionalidade: Autenticação e gestão de acesso
  Como usuário
  Quero me cadastrar, entrar e recuperar acesso
  Para utilizar o portal conforme meu perfil

  # IDs: E2E-04-<seq>  →  espelhado em tests/e2e/test_04_autenticacao.py

  @p0 @functional @e2e-04-001
  Cenário: [E2E-04-001] Visitante acessa a tela de cadastro
    Quando o visitante acessa "/cadastro/"
    Então a página deve carregar com status 200
    E o formulário de cadastro deve estar visível

  @p0 @functional @e2e-04-002
  Cenário: [E2E-04-002] Visitante se cadastra como cliente final e acessa o portal
    Dado que não existe usuário com o e-mail "cliente@teste.com"
    Quando o visitante preenche nome, e-mail "cliente@teste.com", telefone e senhas coincidentes
    E envia o formulário em "/cadastro/"
    Então um usuário com papel "cliente_final" deve ser criado
    E o visitante deve ficar autenticado
    E o visitante deve ser redirecionado para "/portal/"
    E deve ver a mensagem "Cadastro concluído. Seu acesso já está ativo."

  @p1 @functional
  Cenário: Cadastro com dados inválidos não cria usuário
    Quando o visitante tenta se cadastrar com e-mail inválido ou senhas diferentes
    Então nenhum usuário novo deve ser criado
    E o formulário deve exibir erros de validação

  @p1 @functional
  Cenário: Usuário autenticado não acessa novamente a tela de cadastro
    Dado que existe um cliente autenticado
    Quando o cliente acessa "/cadastro/"
    Então o cliente deve ser redirecionado para "/portal/"

  @p0 @functional
  Cenário: Visitante acessa a tela de login
    Quando o visitante acessa "/login/"
    Então a página deve carregar com status 200
    E o formulário de login deve estar visível

  @p0 @functional
  Cenário: Cliente faz login com e-mail e é redirecionado ao portal
    Dado que existe o cliente "cliente@teste.com" com senha válida
    Quando o visitante faz login em "/login/" com e-mail "cliente@teste.com" e senha válida
    Então o visitante deve ser redirecionado para "/portal/"
    E deve ver a mensagem "Acesso realizado com sucesso."

  @p0 @functional
  Cenário: Cliente faz login com nome de usuário
    Dado que existe o cliente com username "cliente@teste.com" e senha válida
    Quando o visitante faz login informando o username e a senha válida
    Então o visitante deve ser autenticado com sucesso
    E deve ser redirecionado para "/portal/"

  @p0 @functional
  Cenário: Administrador faz login e é redirecionado ao painel admin
    Dado que existe um usuário administrador master ativo
    Quando o administrador faz login com credenciais válidas
    Então o usuário deve ser redirecionado para "/painel-admin/"

  @p0 @functional
  Cenário: Supervisor faz login e acessa área administrativa
    Dado que existe um usuário supervisor ativo
    Quando o supervisor faz login com credenciais válidas
    Então o usuário deve ser redirecionado para "/painel-admin/"
    E deve conseguir abrir o painel administrativo

  @p1 @functional
  Cenário: Login com credenciais inválidas é rejeitado
    Quando o visitante tenta fazer login com senha incorreta
    Então o login deve falhar
    E a mensagem "Informe um email/usuário e senha válidos." deve ser exibida
    E o visitante não deve ficar autenticado

  @p0 @functional
  Cenário: Usuário autenticado encerra a sessão com sucesso
    Dado que existe um usuário autenticado
    Quando o usuário acessa "/sair/"
    Então a sessão deve ser encerrada
    E o usuário deve ser redirecionado para "/"
    E deve ver a mensagem "Sessão encerrada com sucesso."

  @p0 @functional
  Cenário: Quando não existe admin o login exibe opção de configurar administrador inicial
    Dado que não existe nenhum administrador no sistema
    Quando o visitante acessa "/login/"
    Então deve existir a opção de configurar o administrador inicial

  @p0 @functional
  Cenário: Visitante cria o administrador master inicial e acessa o painel
    Dado que não existe nenhum administrador no sistema
    Quando o visitante acessa "/configurar-admin/"
    E preenche um cadastro válido de administrador inicial
    Então um usuário master com is_staff e is_superuser deve ser criado
    E o visitante deve ficar autenticado
    E deve ser redirecionado para "/painel-admin/"

  @p0 @functional
  Cenário: Configuração de admin inicial fica bloqueada depois que já existe admin
    Dado que já existe um administrador no sistema
    Quando o visitante acessa "/configurar-admin/"
    Então o visitante deve ser redirecionado para "/login/"
    E deve ver a mensagem informando que o administrador inicial já foi configurado

  @p1 @functional
  Cenário: Login oculta botão de admin inicial quando já existe administrador
    Dado que já existe um administrador no sistema
    Quando o visitante acessa "/login/"
    Então a opção de configurar administrador inicial não deve aparecer

  @p0 @functional
  Cenário: Usuário solicita recuperação de senha com e-mail cadastrado
    Dado que existe o usuário com e-mail "cliente@teste.com"
    Quando o visitante solicita recuperação de senha em "/senha/recuperar/" com "cliente@teste.com"
    Então o visitante deve ser redirecionado para "/senha/recuperar/enviado/"
    E um e-mail de recuperação deve ser enviado para "cliente@teste.com"

  @p1 @functional
  Cenário: Recuperação de senha para e-mail inexistente não envia e-mail
    Quando o visitante solicita recuperação de senha com "naoexiste@teste.com"
    Então a página de confirmação de envio pode ser exibida
    Mas nenhum e-mail de recuperação deve ser enviado

  @p0 @functional
  Cenário: Usuário redefine a senha pelo link válido
    Dado que existe um link válido de redefinição de senha para "cliente@teste.com"
    Quando o usuário abre o link e define uma nova senha válida
    Então a redefinição deve ser concluída com sucesso
    E o usuário deve ser direcionado para "/senha/redefinir/concluido/"

  @p1 @functional
  Cenário: Link inválido ou expirado de redefinição de senha é rejeitado
    Quando o usuário acessa um link de redefinição inválido ou expirado
    Então a redefinição não deve ser permitida
    E uma mensagem de link inválido deve ser exibida

  @p1 @functional
  Cenário: Após redefinir senha o usuário consegue fazer login com a nova senha
    Dado que o usuário "cliente@teste.com" redefiniu a senha para "NovaSenha123"
    Quando o usuário faz login com "cliente@teste.com" e "NovaSenha123"
    Então o login deve ser bem-sucedido
    E o usuário deve acessar a área autenticada correspondente
