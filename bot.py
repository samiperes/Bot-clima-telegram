import os #importando a biblioteca os (operational system) para interagir com o sistema operacional do pc
import requests #importando a biblioteca que é o que faz possível se comunicar com o telegram
from dotenv import load_dotenv #carregando a variável de ambiente para meu código

load_dotenv(".env") #especificamente o arquivo .env

token = os.getenv("TELEGRAM_TOKEN") #pegando o valor da string?var? específica dentro do meu arquivo .env
chave = os.getenv("WEATHERSTACK_KEY") #pegando o valor da string?var? específica dentro do meu arquivo .env

url_telegram = "https://api.telegram.org/bot" + token #abre o link do telegram + meu token. 
url_clima = "http://api.weatherstack.com/current" #abre o link direto da api do weatherstack


def buscar_clima(cidade): #define uma função que busca o clima tendo em base o valor da variável cidade
    dados = requests.get(
        url_clima,
        params={"access_key": chave, "query": cidade, "units": "m"},
        timeout=15, #se passar de 15 para?
    ).json() #pedindo as informações ao Weatherstack

    if "current" not in dados: #se o que for digitado não estiver armazenado nos dados da api
        return "Não consegui encontrar o clima de '" + cidade + "'. Confira o nome e tente novamente." #emite a mensagem anterior

    nome = dados["location"]["name"]
    pais = dados["location"]["country"]
    temperatura = dados["current"]["temperature"]
    sensacao = dados["current"]["feelslike"]
    condicao = ", ".join(dados["current"]["weather_descriptions"])
    umidade = dados["current"]["humidity"]
    vento = dados["current"]["wind_speed"] #pega palavras da mensagem retornada pelo weatherstack e separa em variáveis específicas

    texto = "📍 " + nome + ", " + pais + "\n" #armazena as palavras que interessam junto com um texto montado em variáveis
    texto += "🌡️ Temperatura: " + str(temperatura) + "°C (sensação de " + str(sensacao) + "°C)\n"
    texto += "☁️ Condição: " + condicao + "\n"
    texto += "💧 Umidade: " + str(umidade) + "%\n"
    texto += "💨 Vento: " + str(vento) + " km/h"
    return texto #retorna o texto inteiro em uma mensagem de texto


def enviar_mensagem(chat_id, texto): #define mais uma função para enviar a mensagem
    requests.post(
        url_telegram + "/sendMessage",
        data={"chat_id": chat_id, "text": texto},
        timeout=15,
    )


def tratar_mensagem(chat_id, texto): #define mais uma função para tratar a mensagem do usuário
    texto = texto.strip() #esse .strip remove espaços antes e depois da mensagem

    if texto == "/start" or texto == "/help": #se o texto for algum dos comandos para iniciar
        enviar_mensagem(
            chat_id,
            "Oi! Eu sou o bot do clima ☀️\n\n"
            "Digite o nome de uma cidade (ex: São Paulo) "
            "ou use /clima (nome da cidade) que eu te digo como está o tempo lá.",
        ) #ele envia essa mensagem específica
    elif texto.startswith("/clima"): #se a mensagem for pedindo o clima
        cidade = texto.replace("/clima", "", 1).strip()
        if cidade == "":
            enviar_mensagem(chat_id, "Use assim: /clima São Paulo") #caso a pessoa não tenha digitado nada depois do comando de clima
        else:
            enviar_mensagem(chat_id, buscar_clima(cidade)) #caso tenha preenchido o comando e mais alguma coisa, procura a cidade com base nessa outra coisa
    else:
        enviar_mensagem(chat_id, buscar_clima(texto)) #caso mande só um texto sem comando, assume que é uma cidade e procura


if not token or not chave:
    raise SystemExit("Faltam TELEGRAM_TOKEN ou WEATHERSTACK_KEY no arquivo .env") #confere o token e a chave. se faltar algum, o programa encerra.

print("(O bot está rodando...)") #emite a mensagem que o bot está rodando 
offset = None

while True:
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        resposta = requests.get(url_telegram + "/getUpdates", params=params, timeout=40).json()

        for update in resposta.get("result", []):
            offset = update["update_id"] + 1
            mensagem = update.get("message")
            if mensagem and "text" in mensagem:
                tratar_mensagem(mensagem["chat"]["id"], mensagem["text"])

    except requests.RequestException as erro:
        print("Erro de conexão:", erro)