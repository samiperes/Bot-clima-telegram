import os

import requests
from dotenv import load_dotenv

load_dotenv(".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_KEY = os.getenv("WEATHERSTACK_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
# O plano gratuito da Weatherstack só aceita HTTP (não HTTPS)
WEATHER_URL = "http://api.weatherstack.com/current"

AJUDA = (
    "Olá! Eu sou o bot do clima ☀️\n\n"
    "Me envie o nome de uma cidade (ex: São Paulo) "
    "ou use /clima <cidade> que eu te digo como está o tempo lá."
)


def buscar_clima(cidade):
    """Consulta a API Weatherstack e devolve um texto pronto para enviar."""
    resposta = requests.get(
        WEATHER_URL,
        params={"access_key": WEATHER_KEY, "query": cidade, "units": "m"},
        timeout=15,
    ).json()

    if "current" not in resposta:
        return f"Não consegui encontrar o clima de '{cidade}'. Confira o nome e tente de novo."

    local = resposta["location"]
    atual = resposta["current"]
    descricao = ", ".join(atual["weather_descriptions"])

    return (
        f"📍 {local['name']}, {local['country']}\n"
        f"🌡️ Temperatura: {atual['temperature']}°C "
        f"(sensação de {atual['feelslike']}°C)\n"
        f"☁️ Condição: {descricao}\n"
        f"💧 Umidade: {atual['humidity']}%\n"
        f"💨 Vento: {atual['wind_speed']} km/h"
    )


def enviar_mensagem(chat_id, texto):
    requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        data={"chat_id": chat_id, "text": texto},
        timeout=15,
    )


def tratar_mensagem(chat_id, texto):
    texto = texto.strip()

    if texto in ("/start", "/help"):
        enviar_mensagem(chat_id, AJUDA)
    elif texto.startswith("/clima"):
        cidade = texto.replace("/clima", "", 1).strip()
        if not cidade:
            enviar_mensagem(chat_id, "Use assim: /clima São Paulo")
        else:
            enviar_mensagem(chat_id, buscar_clima(cidade))
    else:
        # qualquer outro texto é tratado como nome de cidade
        enviar_mensagem(chat_id, buscar_clima(texto))


def main():
    if not TELEGRAM_TOKEN or not WEATHER_KEY:
        raise SystemExit("Faltam TELEGRAM_TOKEN ou WEATHERSTACK_KEY no arquivo .env")

    print("Bot rodando... (Ctrl+C para parar)")
    offset = None  # guarda qual foi a última atualização já lida

    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset

            updates = requests.get(
                f"{TELEGRAM_URL}/getUpdates", params=params, timeout=40
            ).json()

            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                mensagem = update.get("message")
                if mensagem and "text" in mensagem:
                    tratar_mensagem(mensagem["chat"]["id"], mensagem["text"])

        except requests.RequestException as erro:
            print("Erro de conexão:", erro)


if __name__ == "__main__":
    main()
