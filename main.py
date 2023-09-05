import scrapy

# Exercício:
# Buscar:
# Nome, ID, Tamanho e Peso
# Alguns dados estão dentro da página do Pokemon
# Página do Pokémon deve usar o parser "parser_pokemon"

# Dica: Principais CSS Selectors:
# https://www.w3schools.com/cssref/css_selectors.php


class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  # def parse(self, response):
  #   titulo = response.css('main#main > h1::text')
  #   titulo_texto = titulo.get()
  #   yield {'titulo': titulo_texto}

  # def parse(self, response):
  #   linhas = response.css('table#pokedex > tbody > tr')
  #   linha = linhas[0]
  #   link = linha.css("td:nth-child(2) > a::attr(href)")
  #   yield response.follow(link.get(), self.parse_pokemon)

  # def parse(self, response):
  #   linhas = response.css('table#pokedex > tbody > tr')
  #   for linha in linhas:
  #     link = linha.css("td:nth-child(2) > a::attr(href)")
  #     yield response.follow(link.get(), self.parse_pokemon)

  # nome peso id e tipo
  # def parse_pokemon(self, response):
  #   id = response.css("table.vitals-table > tbody > tr:nth-child(1) > td > strong::text")
  #   nome = response.css("main#main > h1::text")
  #   peso = response.css('table.vitals-table > tbody > tr:nth-child(5) > td::text')
  #   tipo1 = response.css("table.vitals-table > tbody > tr:nth-child(2) > td > a:nth-child(1)::text")
  #   tipo2 = response.css("table.vitals-table > tbody > tr:nth-child(2) > td > a:nth-child(2)::text")
  #   altura = response.css("table.vitals-table > tbody > tr:nth-child(4) > td::text")
  #   #habilidades1 = response.css("table.vitals-table > tbody > tr:nth-child(6) > td > span::text")
  #   habilidadeEscondida = response.css("table.vitals-table > tbody > tr:nth-child(6) > td > small")

  #   yield {" Id ":id.get()," Url Pokemon ":self.get(), " Nome ":nome.get()," Peso ":peso.get(), " Tipo 1 ":tipo1.get(),"Tipo 2":tipo2.get()," Altura ": altura.get(), " URL Habilidade ": habilidadeEscondida.css("a::attr(href)").get(), " Nome da Habilidade ": habilidadeEscondida.css("a::text").get(), " Descrição Habilidade ":habilidadeEscondida.css("a::attr(title)").get()}

  # class PokeSpider(scrapy.Spider):
  #   name = 'pokespider'
  #   start_urls = ['https://pokemondb.net/pokedex/all']

  #   def parse(self, response):
  #     ### tabela de seletores de CSS
  #     tabela_pokedex = "table#pokedex > tbody > tr"

  #     linhas = response.css(tabela_pokedex)

  #     # Processa uma linha apenas
  #     linha = linhas[0]
  #     coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
  #     yield response.follow(coluna_href.get(), self.parser_pokemon)

  #     # Processa todas as linhas
  #     for linha in linhas:
  #       # coluna_nome = linha.css("td:nth-child(2) > a::text")
  #       # coluna_id = linha.css("td:nth-child(1) > span.infocard-cell-data::text")
  #       #yield {'id': coluna_id.get(),'nome': coluna_nome.get()}

  #       coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
  #       yield response.follow(coluna_href.get(), self.parser_pokemon)

  #   def parser_pokemon(self, response):
  #     id_selector = "table.vitals-table > tbody > tr:nth-child(1) > td > strong::text"

  #     id = response.css(id_selector)
  #     yield {'id': id.get()}
  def parse(self, response):
    # pokemons = response.css('table#pokedex > tbody > tr')
    # for pokemon in pokemons:
    #   link = pokemon.css("td:nth-child(2) > a::attr(href)")
    #   yield response.follow(link.get(), self.parse_pokemon)

    linhas = response.css('table#pokedex > tbody > tr')
    linha = linhas[0]
    link = linha.css("td:nth-child(2) > a::attr(href)")
    yield response.follow(link.get(), self.parse_pokemon)
  
  def parse_pokemon(self, response):
    evolucoes = []
    id = response.css("table.vitals-table > tbody > tr:nth-child(1) > td > strong::text").get()
    nome = response.css("main#main > h1::text").get()
    altura = response.css("table.vitals-table > tbody > tr:nth-child(4) > td::text").get()
    peso = response.css("table.vitals-table > tbody > tr:nth-child(5) > td::text").get()
    tipos = response.css("table.vitals-table > tbody > tr:nth-child(2) > td a.type-icon::text").getall()
    

    tiposPokemon = [tipo.strip() for tipo in tipos if tipo.strip()]
    
    # evolution = response.css('h2:contains("Evolution chart") + div.infocard-list-evo > div.infocard')
    evolucao = response.css("div.infocard-list-evo > div.infocard")

    
    for evolucao_pokemon in evolucao:
      id_evolucao = evolucao_pokemon.css('small::text').get()
      nome_evolucao = evolucao_pokemon.css('a.ent-name::text').get()
      url_evolucao = evolucao_pokemon.css('a.ent-name::attr(href)').get()

      if id_evolucao and nome_evolucao and url_evolucao:
        evolucoes.append({
          'Number': id_evolucao,
          'Name': nome_evolucao,
          'URL': url_evolucao
        })

    ability_links = response.css('table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)').getall()

    for ability_link in ability_links:
      yield response.follow(ability_link,
                            self.parse_ability,
                            meta={
                              'Number': id,
                              'Page URL': response.url,
                              'Name': nome,
                              'Next Evolutions': evolucoes,
                              'Height': altura,
                              'Weight': peso,
                              'Types': tiposPokemon,
                            })

  def parse_ability(self, response):
    ability_name = response.css('h1::text').get()
    ability_description = response.selector.xpath("//div[@class='grid-col span-md-12 span-lg-6']/p/text()").getall()

    cleaned_ability_description = [
      desc.strip() for desc in ability_description if desc.strip()
    ]

    yield {
      'Number': response.meta['Number'],
      'Page URL': response.meta['Page URL'],
      'Name': response.meta['Name'],
      'Next Evolutions': response.meta['Next Evolutions'],
      'Height': response.meta['Height'],
      'Weight': response.meta['Weight'],
      'Types': response.meta['Types'],
      'Ability': {
        'Name': ability_name,
        'URL': response.url,
        'Description': cleaned_ability_description,
      }
    }
