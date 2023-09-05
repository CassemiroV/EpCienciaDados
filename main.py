import scrapy

class PokeSpider(scrapy.Spider):
  name = "pokespider'"
  start_urls = ["https://pokemondb.net/pokedex/all"]

  def parse(self, response):

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
    

    tipos_pokemon = [tipo.strip() for tipo in tipos if tipo.strip()]
    
    evolucao = response.css("div.infocard-list-evo > div.infocard:not(:first-child)")
    for evolucao_pokemon in evolucao:
      id_evolucao = evolucao_pokemon.css('small::text').get()
      nome_evolucao = evolucao_pokemon.css('a.ent-name::text').get()
      url_evolucao = evolucao_pokemon.css('a.ent-name::attr(href)').get()

      if id_evolucao and nome_evolucao and url_evolucao:
        evolucoes.append({
          "Id": id_evolucao,
          'Nome': nome_evolucao,
          'URL': url_evolucao
        })

    url_habilidades = response.css('table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)').getall()

    for url_habilidade in url_habilidades:
      yield response.follow(url_habilidade,
                            self.parse_ability,
                            meta={
                              "Id": id,
                              "URL": response.url,
                              "Nome": nome,
                              "Evolucoes": evolucoes,
                              "Altura": altura,
                              "Peso": peso,
                              "Tipos": tipos_pokemon,
                            })

  
  
  pokemon_data = {}
  def parse_ability(self, response):
    nome_habilidade = response.css("h1::text").get()
    desc_habilidade =' '.join(response.css('div > div > h2:contains("Effect") + p::text').getall())

    yield {
      "Id": response.meta["Id"],
      "URL": response.meta["URL"],
      "Nome": response.meta["Nome"],
      "Evolucoes": response.meta["Evolucoes"],
      "Altura": response.meta["Altura"],
      "Peso": response.meta["Peso"],
      "Tipos": response.meta["Tipos"],
      "Habilidades": {
        "Nome": nome_habilidade,
        "URL": response.url,
        "Descricao": desc_habilidade,
      }
    }
