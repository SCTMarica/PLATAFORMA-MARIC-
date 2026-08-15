# language: pt
Funcionalidade: Notícias, eventos e mídia
  Como visitante
  Quero consultar notícias, eventos e mídias publicadas
  Para me informar sobre as atividades da instituição

  Contexto:
    Dado que o site possui configurações institucionais básicas

  @p0 @functional
  Cenário: Visitante lista notícias publicadas
    Dado que existem notícias publicadas
    Quando o visitante acessa "/noticias/"
    Então a lista deve exibir as notícias publicadas
    E cada item deve permitir abrir o detalhe

  @p0 @functional
  Cenário: Visitante abre o detalhe de uma notícia publicada
    Dado que existe a notícia publicada "Abertura do portal" com slug "abertura-do-portal"
    Quando o visitante acessa "/noticias/abertura-do-portal/"
    Então a página deve exibir o título "Abertura do portal"
    E o conteúdo da notícia deve estar visível

  @p1 @functional
  Cenário: Notícia não publicada não aparece para o visitante
    Dado que existe uma notícia não publicada com slug "rascunho"
    Quando o visitante acessa "/noticias/"
    Então a notícia "rascunho" não deve aparecer na lista
    Quando o visitante acessa "/noticias/rascunho/"
    Então a página deve retornar status 404

  @p1 @functional
  Cenário: Notícia com data futura de publicação não aparece para o visitante
    Dado que existe uma notícia marcada como publicada com data futura e slug "agendada"
    Quando o visitante acessa "/noticias/"
    Então a notícia "agendada" não deve aparecer na lista
    Quando o visitante acessa "/noticias/agendada/"
    Então a página deve retornar status 404

  @p1 @functional
  Cenário: Lista de notícias pagina os resultados
    Dado que existem mais de 9 notícias publicadas
    Quando o visitante acessa "/noticias/"
    Então a primeira página deve listar no máximo 9 notícias
    E a paginação deve permitir ir para a página seguinte

  @p0 @functional
  Cenário: Visitante lista eventos publicados
    Dado que existem eventos publicados
    Quando o visitante acessa "/eventos/"
    Então a lista deve exibir os eventos publicados

  @p0 @functional
  Cenário: Visitante abre o detalhe de um evento publicado
    Dado que existe o evento publicado "Feira cultural" com slug "feira-cultural"
    Quando o visitante acessa "/eventos/feira-cultural/"
    Então a página deve exibir o título "Feira cultural"
    E a data e a descrição do evento devem estar visíveis

  @p0 @functional
  Cenário: Visitante acessa o calendário de eventos
    Quando o visitante acessa "/eventos/calendario/"
    Então a página deve carregar com status 200
    E o calendário do mês atual deve estar visível

  @p1 @functional
  Cenário: Calendário exibe eventos do mês selecionado
    Dado que existe um evento publicado no mês corrente
    E que existe um evento publicado em outro mês
    Quando o visitante acessa o calendário do mês corrente
    Então apenas o evento do mês corrente deve aparecer no calendário

  @p1 @functional
  Cenário: Lista de eventos oferece link para o calendário
    Quando o visitante acessa "/eventos/"
    Então deve existir um link para "/eventos/calendario/"
    Quando o visitante abre esse link
    Então a página do calendário deve carregar com status 200

  @p1 @functional
  Cenário: Evento não publicado não aparece para o visitante
    Dado que existe um evento não publicado com slug "evento-oculto"
    Quando o visitante acessa "/eventos/"
    Então o evento "evento-oculto" não deve aparecer na lista
    Quando o visitante acessa "/eventos/evento-oculto/"
    Então a página deve retornar status 404

  @p1 @functional
  Cenário: Visitante acessa a página de mídia
    Quando o visitante acessa "/midia/"
    Então a página deve carregar com status 200

  @p1 @functional
  Cenário: Página de mídia lista vídeos ativos
    Dado que existem vídeos ativos cadastrados
    Quando o visitante acessa "/midia/"
    Então os vídeos ativos devem ser listados

  @p1 @functional
  Cenário: Página de mídia lista itens de galeria ativos
    Dado que existem itens de galeria ativos cadastrados
    Quando o visitante acessa "/midia/"
    Então os itens de galeria ativos devem ser listados

  @p2 @functional
  Cenário: Mídia inativa não aparece para o visitante
    Dado que existem mídias inativas dos tipos vídeo e galeria
    Quando o visitante acessa "/midia/"
    Então as mídias inativas não devem ser exibidas
