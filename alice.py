import unidecode
import string
import pandas as pd
import requests
import time
from ztools import ztext
from chatterbot import ChatBot
import re
from Calendar import myCalendar as myCalendar
from chatterbot.response_selection import get_random_response
import uracrawler as ura
from database import DataBase
from zcrawler import ZCrawler

chatbot = ChatBot(
    "Alice",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=["chatterbot.logic.BestMatch",],
    database="./database.sqlite3",
    response_selection_method=get_random_response,
    filters=["chatterbot.filters.RepetitiveResponseFilter"],
    read_only=False,
)


class Chatbot:
    def __init__(self, name="Alice"):
        self.name = name
        self.user = None
        self.answer = ""
        self.adapters = [
            self.Cancelar,
            self.Agradecimento,
            self.Ituverava_covid,
            self.Today_events,
            self.Next_events,
            self.Today_holidays,
            self.Next_holidays,
            self.Kinoplex,
            self.Cinemais,
            self.Cinema,
            self.Bitcoin_forecast_play,
            self.Bitcoin_forecast,
            self.Bitcoin_limit,
            self.Bitcoin_nowvalue,
            self.Download_youtube,
            self.Invert,
            self.Sair,
            self.Talk,
        ]
        self.classes = {
            "quest": [
                "qual",
                "quais",
                "como",
                "pode",
                "mostre",
                "poderia",
                "gostaria",
                "quero",
                "preciso",
                "que",
                "quando",
                "onde",
                "quanto",
                "quantos",
                "algum",
                "alguns",
            ],
            "calendario": ["eventos", "agenda", "calendario", "compromissos", "compromisso", "evento"],
            "male": ["masculino", "male", "m", "homem", "macho", "man"],
            "female": ["feminino", "female", "f", "w", "mulher", "femea", "woman"],
            "bitcoin": ["bitcoin", "bitplay", "bitscript", "criptomoeda"],
            "movie": ["filme", "filmes"],
            "cinemais": ["cinemais"],
            "kinoplex": ["kinoplex"],
            "emergencia": ["emergencia", "help", "socorro", "ajuda"],
            "cop": [
                "policia",
                "crime",
                "assalto",
                "sequestro",
                "roubo",
                "roubaram",
                "sequestraram",
                "assaltaram",
                "assaltou",
                "policial",
                "sequestrar",
                "roubar",
                "viatura",
                "assaltado",
            ],
            "fireman": ["bombeiro", "bombeiros", "incendio", "fogo", "explosao"],
            "amb": [
                "ambulancia",
                "medico",
                "doente",
                "hospital",
                "clinica",
                "mal",
                "desmaio",
                "desmaiei",
                "desmaiou",
                "acidente",
                "acidentou",
                "acidentado",
                "quebrou",
                "morrendo",
                "morrer",
                "infarto",
                "enfarto",
                "avc",
                "quebrou",
                "quebrei",
                "pulso",
                "pulsação",
            ],
            "venda": ["vender", "vende", "venda"],
            "compra": ["comprar", "compra"],
            "duvida": ["duvida", "questionamento", "pergunta", "saber", "sabe", "pregunta"],
            "intenção": ["quero", "desejo", "preciso", "vou"],
            "sair": ["sair"],
            "sim": ["sim", "positivo", "claro", "isso", "confirma", "confirmo", "s", "sm"],
            "nao": ["nao", "negativo", "n"],
            "agradecimento": ["valeu", "obrigado", "obrigada", "brigado", "vlw"],
            "mostrar": [
                "ver",
                "saber",
                "exibir",
                "mostrar",
                "classe",
                "classifico",
                "classificacao",
                "classificado",
                "classifica",
                "classificar",
                "qualifica",
                "preco",
                "custo",
                "lucro",
                "cotacao",
                "vender",
                "vende",
                "vendo",
                "venda",
            ],
            "cancelar": ["cancelar", "cancela", "outro", "errado"],
            "today": ["today", "hoje", "agora"],
            "event": ["evento", "compromisso", "eventos"],
            "next": ["proximo", "proximos", "seguir", "futuro", "futuros", "previsto", "previstos"],
            "holiday": ["feriado", "ferias", "folga", "feriados"],
            "shopping": ["shopping", "shoppings"],
            "praca": ["praca", "novo", "menor"],
            "urashopping": ["uberaba", "center", "antigo", "velho", "maior"],
            "filme": ["filme", "filmes", "movie", "movies", "cinema", "cinemas"],
            "loja": ["lojas", "estabelecimentos", "loja", "estabelecimento"],
            "clima": ["clima", "tempo", "previsao", "weather", "chover", "chuva", "sol", "temperatura"],
            "news": ["noticia", "noticias", "novidade", "novidades", "jornal"],
            "turnoff": ["desativar", "off", "parar", "pare", "desative"],
            "turnon": ["ativar", "ligar", "começar", "start", "ative", "ligue"],
            "notify": ["notificacao", "notificacoes", "notificar", "alerta", "alertas"],
            "bitcoin": ["bitcoin", "btc", "btcbrl", "criptomoeda", "bitcoins", "cripo", "criptomoedas"],
            "forecast": ["previsao", "estimativa"],
            "limit": ["limit", "limite", "marca", "marcacao"],
            "video": ["video", "filme", "clip", "trailer"],
            "audio": ["audio", "musica", "mp3", "som", "music"],
            "download": ["download", "baixar", "baixe"],
            "playlist": ["playlist"],
            "covid": ["covid", "covid19", "corona", "coronavirus", "sarscov2", "cov"],
            "info": [
                "informacao",
                "info",
                "informativo",
                "relatorio",
                "atualizacao",
                "informe",
                "fale",
                "informa",
                "relate",
                "relacao",
            ],
        }
        self.chats = {}
        self.classification = []
        self.commands = []
        self.send_cep = None

    def ClearText(self, text):
        # stemmer = nltk.stem.RSLPStemmer()
        if type(text) == str:
            x = text.split()
        else:
            x = text
        if type(x) == list:
            newx = list()
            for word in x:
                w = word.lower()
                w = unidecode.unidecode(w)
                for c in list(string.punctuation):
                    w = w.replace(c, " ")
                if len(w) > 0:
                    if w[-1] == " ":
                        w = w[:-1]
                    # print('{} -> {}'.format(word, w))
                newx.append(w)
            text = " ".join(newx)
        else:
            text = " ".join(text)
        return text

    def insert(self, message):
        if user not in self.chats.keys():
            self.chats[user] = [message]
        else:
            self.chats[user].append(message)

    def address(self, ans):
        if not any(x == "ituverava" for x in ztext.ClearText(ans).split()):
            ans += " ituverava"
        geolocator = Nominatim(user_agent="monica_bot")
        location = geolocator.geocode(ans)
        if location:
            location = location[0].split(", ")[0]
        return location

    def youtube_link(self, ans):
        for term in ans.split():
            if "youtube.com" in term:
                return term
            if "watch?" in term:
                return term
        return None

    def number(self, ans):
        num = re.findall(r"\d+", ans)
        if len(num) > 0:
            if len(num) == 2 or len(num) == 1:
                return float(".".join(num))
            else:
                return float(num[0])
        return None

    def send(self, ans):
        # self.answer = 'Zeca: ' + ans
        self.answer = ans
        return self.answer

    def start_talk(self):
        self.send("Olá! Como posso te ajudar?")
        return self.answer

    def classific(self, message):
        for word in self.classes.keys():
            if any(x in self.classes[word] for x in self.ClearText(message).split()):
                self.classification.append(word)

        for word in message.split():
            if word[:2] == "--":
                self.commands.append(f'{self.ClearText(word).replace(" ", "")}')

    def get_response(self, message):
        self.classific(message)
        for adap in self.adapters:
            ans = adap(message)
            if ans:
                return self.send(ans)

    def match(self, reqs=None, comms=None):
        if reqs:
            if all(x in self.classification for x in reqs):
                return True
        if comms:
            if all(x in self.commands for x in comms):
                return True

        return False

    def Cancelar(self, message):
        reqs = ["cancelar"]
        answer = []
        if self.match(reqs):
            answer.append(("msg", "Tudo bem. Como posso te ajudar então?"))
            self.classification = []
            return answer

    def Agradecimento(self, message):
        reqs = ["agradecimento"]
        answers = []
        if self.match(reqs):
            answer = "Se precisar, é só chamar."
            blocks = ["agradecimento"]
            self.classification = list(filter(lambda a: a not in blocks, self.classification))
            answers.append(("msg", answer))
            return answers

    def Ituverava_covid(self, message):
        reqs = ["covid", "info"]
        comms = ["covid", "info"]
        answers = []
        if self.match(reqs, comms):
            crawler = ZCrawler()
            crawler.ituv_info_covid()
            answer1 = "Aqui está:"
            answer2 = open("Ituverava/ituv_info_covid.png", "rb")
            answers.append(("msg", answer1))
            answers.append(("img", answer2))
            self.classification = []
            self.commands = []
            return answers

    def Today_events(self, message):
        reqs = ["event", "today"]
        answers = []
        if self.match(reqs):
            events = myCalendar.today_events()
            if len(events) == 0:
                answer = "Você não tem nenhum evento para hoje!"
            else:
                answer = "Estes são seus eventos de hoje:\n"
                for event in events:
                    answer += "\n{} - {}".format(event["start"], event["name"])
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Next_events(self, message):
        reqs = ["event"]
        answers = []
        if self.match(reqs):
            events = myCalendar.next_events()
            if len(events) == 0:
                answer = "Você não tem nenhum evento previsto."
            else:
                answer = "Estes são seus próximos eventos:\n"
                for event in events:
                    answer += "\n{} - {}".format(event["start"], event["name"])
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Today_holidays(self, message):
        reqs = ["holiday", "today"]
        answers = []
        if self.match(reqs):
            events = myCalendar.today_events(Id=myCalendar.holidays_id)
            if len(events) == 0:
                answer = "Nós não temos nenhum feriado hoje!"
            else:
                answer = "Este é o nosso feriado de hoje:\n"
                for event in events:
                    answer += "\n{} - {}".format(event["start"], event["name"])
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Next_holidays(self, message):
        reqs = ["holiday"]
        answers = []
        if self.match(reqs):
            events = myCalendar.next_events(Id=myCalendar.holidays_id)
            if len(events) == 0:
                answer = "Nós não temos nenhum feriado previsto."
            else:
                answer = "Estes são nossos próximos feriados:\n"
                for event in events:
                    answer += "\n{} - {}".format(event["start"], event["name"])
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Kinoplex(self, message):
        reqs = ["kinoplex"]
        answers = []
        if self.match(reqs):
            movies = ura.kinoplex()
            if len(movies) > 0:
                answer = "Estes são os filmes que estão passando no Kinoplex Uberaba:\n\n"
                for movie in movies:
                    answer += f" - {movie}\n"
            else:
                answer = "Não achei nenhum filme disponível no Kinoplex Uberaba hoje."
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Cinemais(self, message):
        reqs = ["cinemais"]
        answers = []
        if self.match(reqs):
            movies = ura.cinemais()
            if len(movies) > 0:
                answer = "Estes são os filmes que estão passando no Cinemais Uberaba:\n\n"
                for movie in movies:
                    answer += f" - {movie}\n"
            else:
                answer = "Não achei nenhum filme disponível no Cinemais Uberaba hoje."
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Cinema(self, message):
        reqs = ["filme"]
        answers = []
        if self.match(reqs):
            answer = "Temos dois cinemas em Uberaba:\n"
            answer += " - Cinemais\n"
            answer += " - Kinoplex\n\n"
            answer += "Sobre qual deseja saber?"
            answers.append(("msg", answer))
            return answers

    def Bitcoin_forecast_play(self, message):
        reqs = ["bitcoin", "forecast", "play"]
        comms = ["btcforecast", "play"]
        answers = []
        if self.match(reqs, comms):
            if "usd" in ztext.ClearText(message).split():
                from Bitcoin.bitscript import play

                nvers = 213
            else:
                from Bitcoin.bitscript_brl import play

                nvers = 755
            user_nvers = self.number(message)
            if user_nvers:
                nvers = user_nvers
            print(f"Usando modelos {nvers}")
            answers.append(("msg", play(plot=True, nvers=nvers)))
            graphic = open("Bitcoin/bitgraphic.png", "rb")
            answers.append(("msg", "Veja o gráfico das previsões:"))
            answers.append(("img", graphic))
            self.classification = []
            self.commands = []
            return answers

    def Bitcoin_forecast(self, message):
        reqs = ["bitcoin", "forecast"]
        comms = ["btcforecast"]
        answers = []
        if self.match(reqs, comms):
            answers.append(("msg", "Fazendo cálculos..."))
            answers.append(())
            self.classification.append("play")
            self.commands.append("play")
            return answers

    def Bitcoin_limit(self, message):
        reqs = ["bitcoin", "limit"]
        comms = ["btclimit"]
        answers = []
        if self.match(reqs, comms):
            import socket

            HOST = "127.0.0.1"  # The server's hostname or IP address
            PORT = 8844  # The port used by the server

            limit = self.number(message)
            if limit:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(b"%f" % limit)
                answer = f"Limite definido para R$ {limit}."
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(b"stop")
                answer = f"Limite cancelado."
            answers.append(("msg", answer))
            self.classification = []
            self.commands = []
            return answers

    def Bitcoin_nowvalue(self, message):
        reqs = ["bitcoin"]
        answers = []
        if self.match(reqs):
            from Bitcoin.bitscript_brl import now_value

            r = now_value()
            date = f"{r[0].tm_mday}/{r[0].tm_mon}/{r[0].tm_year} às {r[0].tm_hour}:{r[0].tm_min}:{r[0].tm_sec}"
            answer = f"{date}.\nBTC: R${r[1]}"
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Download_youtube(self, message):
        reqs = ["download"]
        comms = ["download"]
        answers = []
        if self.match(reqs, comms):
            yt_link = self.youtube_link(message)
            if yt_link:
                from ztube import Download_video

                reqs1 = ["audio"]
                comms1 = ["audio"]

                only_audio = False
                if self.match(reqs1, comms1):
                    only_audio = True

                reqs2 = ["playlist"]
                comms2 = ["playlist"]

                if self.match(reqs2, comms2):
                    done = Download_playlist(yt_link, only_audio=only_audio)
                    if done:
                        answer = "Pronto! Playlist baixada com sucesso."
                    else:
                        answer = "Não foi possível realizar o download."
                else:
                    done = Download_video(yt_link, only_audio=only_audio)
                    if done:
                        answer = "Pronto! Video baixado com sucesso."
                    else:
                        answer = "Não foi possível realizar o download."
                self.classification = []
                self.commands = []
            else:
                answer = "Qual o link do video?"
            answers.append(("msg", answer))
            return answers

    def Invert(self, message):
        comms = ["invert"]
        answers = []
        if self.match(comms=comms):
            words = message.split()
            words.remove("--invert")
            answer = " ".join(words)[::-1]
            answers.append(("msg", answer))
            self.comms = []
            return answers

    def Sair(self, message):
        reqs = ["sair"]
        answers = []
        if self.match(reqs):
            answer = "Espero ter ajudado. Até mais!"
            answers.append(("msg", answer))
            self.classification = []
            return answers

    def Talk(self, message):
        answers = []
        answer = chatbot.get_response(message)
        answers.append(("msg", answer))
        return answers
