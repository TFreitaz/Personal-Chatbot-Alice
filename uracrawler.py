def fixed(name):
    name = name.replace("Ã³", "ó").replace("Ã§", "ç").replace("Ã©", "é").replace("Ã“", "Ó")
    return name


def clean(name):
    name = name.replace("\n", "")
    while "  " in name:
        name = name.replace("  ", " ")
    return name


def praca_shopping():
    from robobrowser import RoboBrowser

    browser = RoboBrowser(parser="html.parser")

    not_finded = 0
    n = 0
    names = set()
    while not_finded < 20:
        # print(f'Página {n}')
        finded = False
        url = f"http://www.pracauberabashopping.com.br/filtro_loja_tipo.asp?tipo=vlojas.asp?busca1={n}"
        browser.open(url)
        item = browser.find("strong")
        if item:
            name = item.text
            if name != "Busca sem resultado.":
                names.add(fixed(name))
                finded = True
        else:
            items = browser.find_all("a")
            if len(items) > 1:
                for item in items[1:]:
                    if item.text != "Resultado da Busca":
                        names.add(fixed(item.text))
                finded = True

        if not finded:
            not_finded += 1

        n += 1
    return names


def news():
    from robobrowser import RoboBrowser

    browser = RoboBrowser(parser="html.parser")
    url = "https://www.jornaldeuberaba.com.br/ultimas-noticias"
    browser.open(url)

    noticias = []
    result = browser.find(class_="lista-registros-interno").find_all("a")

    for noticia in result:
        noticia_parts = []
        items = noticia.find_all("span")
        for item in items:
            noticia_parts.append(item.text)
        noticias.append(noticia_parts)

    return noticias


def kinoplex():
    import requests
    from bs4 import BeautifulSoup

    link = "https://www.kinoplex.com.br/cinema/comparacao/?cinemas=46"
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    body = soup.find_all("body")
    programacoes = body[0].find_all(id="programacoes")
    container = programacoes[0].find_all(class_="container bloco-comparacao")
    carousel = container[0].find_all(class_="cinema-programacao comparacao")
    movies = set()
    for i in range(3, len(carousel), 3):
        movie = str(
            container[0]
            .find_all(class_="cinema-programacao comparacao")[i]
            .find_all(class_="panel panel-default")[0]
            .find_all(class_="panel-heading")[0]
        )
        movie = movie[50:].split("<")[0]
        movies.add(movie)

    return movies


def cinemais():
    from robobrowser import RoboBrowser

    browser = RoboBrowser(parser="html.parser")

    url = "http://www.cinemais.com.br/programacao/cinema.php?cc=9"
    browser.open(url)
    items = browser.find(class_="tableContentIn").find("table").find_all("a")
    movies = set()
    for item in items:
        movies.add(item.text)

    return movies


def uberaba_shopping():

    from robobrowser import RoboBrowser

    browser = RoboBrowser(parser="html.parser")

    url = "https://www.shoppinguberaba.com.br/lojas"
    browser.open(url)

    names = []
    items = browser.find_all(class_="select-items")[1].find_all("li")
    for item in items[1:]:
        name = clean(item.text)
        names.append(name)

    return names


def weather():
    from robobrowser import RoboBrowser
    import json

    browser = RoboBrowser(parser="html.parser")
    key = ""  # Requires a HG Brasil key
    url = f"https://api.hgbrasil.com/weather?key={key}&city_name=Uberaba,MG"
    r = browser.session.get(url)
    result = json.loads(r.content)
    return result
