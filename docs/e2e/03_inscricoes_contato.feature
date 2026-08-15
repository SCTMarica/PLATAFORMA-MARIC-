# language: pt
Funcionalidade: Inscrições e contato
  Como visitante
  Quero me inscrever em formulários e enviar mensagens
  Para participar de atividades e falar com a instituição

  Contexto:
    Dado que o site possui configurações institucionais básicas

  @p0 @functional
  Cenário: Visitante lista formulários de inscrição ativos
    Dado que existem formulários de inscrição ativos
    Quando o visitante acessa "/inscreva-se/"
    Então a lista deve exibir apenas os formulários ativos

  @p0 @functional
  Cenário: Visitante abre um formulário de inscrição ativo
    Dado que existe o formulário ativo "Cadastro geral" com slug "cadastro-geral"
    Quando o visitante acessa "/inscreva-se/cadastro-geral/"
    Então a página deve carregar o formulário "Cadastro geral"
    E os campos definidos no formulário devem estar visíveis

  @p0 @functional
  Cenário: Visitante envia inscrição válida e recebe ID de cadastro
    Dado que existe o formulário ativo "Cadastro geral" com slug "cadastro-geral"
    Quando o visitante preenche os campos obrigatórios válidos
    E envia o formulário em "/inscreva-se/cadastro-geral/"
    Então o visitante deve ser redirecionado para "/inscreva-se/"
    E deve ver uma mensagem de sucesso contendo um ID de cadastro no formato "MARICA-ANO-XXXXX"

  @p0 @functional
  Cenário: Inscrição enviada é persistida no banco
    Dado que existe o formulário ativo "Cadastro geral" com slug "cadastro-geral"
    Quando o visitante envia uma inscrição válida
    Então deve existir um registro de inscrição associado ao formulário
    E o registro deve conter os dados enviados
    E o registro deve conter o campo "id_cadastro"

  @p1 @functional
  Cenário: Formulário inativo não pode ser aberto pelo visitante
    Dado que existe o formulário inativo "Encerrado" com slug "encerrado"
    Quando o visitante acessa "/inscreva-se/"
    Então o formulário "Encerrado" não deve aparecer na lista
    Quando o visitante acessa "/inscreva-se/encerrado/"
    Então a página deve retornar status 404

  @p1 @functional
  Cenário: Visitante não consegue enviar inscrição com campos obrigatórios vazios
    Dado que existe um formulário ativo com campos obrigatórios
    Quando o visitante tenta enviar o formulário sem preencher os obrigatórios
    Então a inscrição não deve ser criada
    E o visitante deve permanecer na página do formulário com erro de validação

  @p1 @functional
  Cenário: Inscrição com upload registra o nome do arquivo enviado
    Dado que existe um formulário ativo com campo de arquivo
    Quando o visitante envia a inscrição anexando o arquivo "documento.pdf"
    Então a inscrição salva deve conter "documento.pdf" nos dados

  @p0 @functional
  Cenário: Visitante acessa a página de contato
    Quando o visitante acessa "/contato/"
    Então a página deve carregar com status 200
    E o formulário de contato deve estar visível

  @p0 @functional
  Cenário: Visitante envia mensagem de contato válida
    Quando o visitante preenche nome, e-mail, assunto e mensagem válidos
    E envia o formulário em "/contato/"
    Então o visitante deve ser redirecionado para "/contato/"
    E deve ver a mensagem "Mensagem enviada com sucesso! Entraremos em contato em breve."

  @p0 @functional
  Cenário: Mensagem de contato é persistida no banco
    Quando o visitante envia uma mensagem de contato válida
    Então deve existir um registro de ContactMessage com os dados enviados
    E o status da mensagem deve ser "nova"

  @p1 @functional
  Cenário: Contato válido dispara e-mail para destino configurado
    Dado que o site possui "contact_email_destination" configurado
    Quando o visitante envia uma mensagem de contato válida
    Então um e-mail deve ser enviado para o destino configurado
    E o assunto do e-mail deve conter o assunto da mensagem

  @p1 @functional
  Cenário: Contato usa e-mail de contato quando destino específico está vazio
    Dado que o site possui "contact_email" configurado
    E que "contact_email_destination" está vazio
    Quando o visitante envia uma mensagem de contato válida
    Então um e-mail deve ser enviado para o "contact_email"

  @p1 @functional
  Cenário: Visitante não consegue enviar contato com dados inválidos
    Quando o visitante envia o formulário de contato com e-mail inválido ou campos vazios
    Então a mensagem não deve ser criada
    E o visitante deve ver erros de validação

  @p2 @functional
  Cenário: Após envio de contato o visitante vê mensagem de sucesso
    Quando o visitante envia uma mensagem de contato válida
    Então a mensagem de sucesso deve aparecer na interface
    E o formulário deve estar disponível novamente para um novo envio
