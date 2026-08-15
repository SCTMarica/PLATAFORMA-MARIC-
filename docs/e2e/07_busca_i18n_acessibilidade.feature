# language: pt
Funcionalidade: Busca, idioma e acessibilidade
  Como visitante
  Quero buscar conteúdo, trocar idioma e ajustar a interface
  Para navegar com mais facilidade

  Contexto:
    Dado que o site possui configurações institucionais básicas

  @p0 @functional
  Cenário: Visitante busca conteúdo e vê resultados de notícias
    Dado que existe a notícia publicada "Feira de ciências"
    Quando o visitante acessa "/busca/?q=feira"
    Então os resultados devem incluir a notícia "Feira de ciências"

  @p0 @functional
  Cenário: Visitante busca conteúdo e vê resultados de eventos
    Dado que existe o evento publicado "Feira cultural"
    Quando o visitante acessa "/busca/?q=cultural"
    Então os resultados devem incluir o evento "Feira cultural"

  @p0 @functional
  Cenário: Visitante busca conteúdo e vê resultados de formulários
    Dado que existe o formulário ativo "Inscrição cultural"
    Quando o visitante acessa "/busca/?q=inscrição"
    Então os resultados devem incluir o formulário "Inscrição cultural"

  @p1 @functional
  Cenário: Busca sem termo não retorna resultados
    Quando o visitante acessa "/busca/" sem parâmetro "q"
    Então a página deve carregar com status 200
    E o total de resultados deve ser 0

  @p1 @functional
  Cenário: Busca sem correspondência informa ausência de resultados
    Quando o visitante acessa "/busca/?q=xyzsemresultado"
    Então nenhum resultado de notícia, evento ou formulário deve ser listado
    E a interface deve indicar ausência de resultados

  @p1 @functional
  Cenário: Busca não retorna notícias ou eventos não publicados
    Dado que existe uma notícia não publicada contendo o termo "secreto"
    E que existe um evento não publicado contendo o termo "secreto"
    Quando o visitante acessa "/busca/?q=secreto"
    Então a notícia não publicada não deve aparecer
    E o evento não publicado não deve aparecer

  @p0 @functional
  Cenário: Visitante troca o idioma do site
    Dado que o visitante está em uma página pública
    Quando o visitante envia o seletor de idioma para "en"
    Então o idioma da sessão deve ficar como "en"
    E a interface deve refletir o idioma selecionado

  @p0 @functional
  Cenário: Idioma selecionado permanece na sessão ao navegar
    Dado que o visitante selecionou o idioma "en"
    Quando o visitante navega para "/sobre/"
    Então o idioma da sessão deve continuar "en"

  @p1 @functional
  Cenário: Rótulos da interface respeitam o idioma selecionado
    Dado que o visitante selecionou o idioma "en"
    Quando o visitante acessa "/"
    Então os rótulos traduzíveis da interface devem aparecer em inglês

  @p2 @functional
  Cenário: Troca de idioma com next inválido redireciona para a home
    Quando o visitante troca o idioma enviando um "next" para domínio externo
    Então o visitante deve ser redirecionado para "/"
    E o idioma selecionado deve ser aplicado na sessão

  @p1 @functional
  Cenário: Visitante alterna entre tema claro e escuro
    Dado que o visitante está em uma página pública
    Quando o visitante aciona o botão de alternar tema
    Então o tema da interface deve mudar entre claro e escuro

  @p1 @functional
  Cenário: Preferência de tema permanece ao recarregar a página
    Dado que o visitante selecionou o tema escuro
    Quando o visitante recarrega a página
    Então o tema escuro deve permanecer ativo

  @p1 @functional
  Cenário: Visitante aumenta o tamanho da fonte
    Dado que o visitante está em uma página pública
    Quando o visitante aciona o controle "A+"
    Então o tamanho da fonte da interface deve aumentar

  @p1 @functional
  Cenário: Visitante diminui o tamanho da fonte
    Dado que o tamanho da fonte já foi aumentado
    Quando o visitante aciona o controle "A-"
    Então o tamanho da fonte da interface deve diminuir

  @p1 @functional
  Cenário: Visitante restaura o tamanho padrão da fonte
    Dado que o tamanho da fonte foi alterado
    Quando o visitante aciona o controle de restaurar fonte
    Então o tamanho da fonte deve voltar para 100%

  @p2 @functional
  Cenário: Widget VLibras está disponível nas páginas públicas
    Quando o visitante acessa "/"
    Então o widget VLibras deve estar presente na página
