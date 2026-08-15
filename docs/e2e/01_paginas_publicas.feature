# language: pt
Funcionalidade: Páginas públicas institucionais
  Como visitante
  Quero navegar pelo site institucional
  Para conhecer a instituição e encontrar informações básicas

  Contexto:
    Dado que o site possui configurações institucionais básicas

  @p0 @functional
  Cenário: Visitante acessa a página inicial
    Quando o visitante acessa "/"
    Então a página deve carregar com status 200
    E o cabeçalho e o rodapé devem estar visíveis

  @p0 @functional
  Cenário: Página inicial exibe banners ativos do carrossel
    Dado que existem banners ativos cadastrados no carrossel
    E que existe um banner inativo cadastrado
    Quando o visitante acessa "/"
    Então apenas os banners ativos devem aparecer no carrossel
    E o banner inativo não deve ser exibido

  @p0 @functional
  Cenário: Página inicial exibe notícias em destaque publicadas
    Dado que existem notícias publicadas marcadas como destaque
    E que existe uma notícia não publicada
    Quando o visitante acessa "/"
    Então as notícias em destaque publicadas devem aparecer na home
    E a notícia não publicada não deve aparecer

  @p0 @functional
  Cenário: Página inicial exibe próximos eventos publicados
    Dado que existem eventos publicados com data futura
    E que existe um evento não publicado
    Quando o visitante acessa "/"
    Então os próximos eventos publicados devem aparecer na home
    E o evento não publicado não deve aparecer

  @p1 @functional
  Cenário: Página inicial lista formulários de inscrição ativos
    Dado que existem formulários de inscrição ativos
    E que existe um formulário de inscrição inativo
    Quando o visitante acessa "/"
    Então os formulários ativos devem aparecer na home
    E o formulário inativo não deve aparecer

  @p1 @functional
  Cenário: Página inicial usa branding configurado no site
    Dado que as configurações do site definem nome, hero e cores
    Quando o visitante acessa "/"
    Então o nome do site configurado deve aparecer no cabeçalho
    E o título e subtítulo do hero devem refletir as configurações

  @p0 @functional
  Cenário: Visitante acessa a página Sobre
    Quando o visitante acessa "/sobre/"
    Então a página deve carregar com status 200
    E o conteúdo da seção institucional deve estar visível

  @p1 @functional
  Cenário: Página Sobre exibe conteúdo institucional configurado
    Dado que as configurações do site possuem título e texto "Sobre"
    Quando o visitante acessa "/sobre/"
    Então o título configurado deve ser exibido
    E o texto institucional configurado deve ser exibido

  @p1 @functional
  Cenário: Visitante acessa Links úteis
    Quando o visitante acessa "/links/"
    Então a página deve carregar com status 200

  @p1 @functional
  Cenário: Visitante acessa a página de Arquivos
    Quando o visitante acessa "/arquivos/"
    Então a página deve carregar com status 200

  @p1 @functional
  Cenário: Menu de navegação leva às seções principais
    Dado que o visitante está na página inicial
    Quando o visitante navega pelo menu para "Sobre", "Notícias", "Eventos", "Mídia", "Links" e "Contato"
    Então cada seção correspondente deve abrir corretamente

  @p2 @functional
  Cenário: Botão voltar aparece fora da página inicial
    Dado que o visitante está em "/noticias/"
    Então o botão de voltar deve estar visível no cabeçalho
    Quando o visitante está em "/"
    Então o botão de voltar não deve estar visível

  @p2 @functional
  Cenário: Menu mobile abre e fecha a navegação
    Dado que o visitante está em viewport mobile
    Quando o visitante abre o menu pelo botão de navegação
    Então os itens do menu devem ficar visíveis
    Quando o visitante fecha o menu
    Então os itens do menu devem ficar ocultos
