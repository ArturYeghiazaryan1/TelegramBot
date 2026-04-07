from telebot import TeleBot
from dotenv import load_dotenv
import os
import requests

load_dotenv()

bot = TeleBot(os.getenv('TOKEN'))

CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/AMD"
METALS_API = "https://api.metals.live/v1/spot"


def get_rates():
    try:
        response = requests.get(CURRENCY_API)
        data = response.json()

        rates = data["rates"]

        usd = round(1 / rates["USD"], 2)
        eur = round(1 / rates["EUR"], 2)
        rub = round(1 / rates["RUB"], 4)

        return usd, eur, rub

    except Exception:
        return None


def get_metals(usd_to_amd):
    try:
        response = requests.get(METALS_API)
        data = response.json()

        # формат: [{"gold": 2180.5}, {"silver": 24.3}, ...]
        gold_usd = next(item["gold"] for item in data if "gold" in item)
        silver_usd = next(item["silver"] for item in data if "silver" in item)

        # перевод в AMD
        gold_amd = round(gold_usd * usd_to_amd, 2)
        silver_amd = round(silver_usd * usd_to_amd, 2)

        return gold_amd, silver_amd

    except Exception:
        return None


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "💱 Բարի գալուստ!\nՍեղմիր /rates ստանալու համար փոխարժեքները"
    )


@bot.message_handler(commands=['rates'])
def rates(message):
    result = get_rates()

    if result:
        usd, eur, rub = result

        metals = get_metals(usd)

        text = f"""
💱 Փոխարժեքներ (AMD):

🇺🇸 USD → {usd} AMD  
🇪🇺 EUR → {eur} AMD  
🇷🇺 RUB → {rub} AMD  
🇷🇺 Outlander → {rub} GOLD  
"""

        if metals:
            gold, silver = metals
            text += f"""

🪙 Մետաղներ:

🥇 Gold → {gold} AMD (per oz)  
🥈 Silver → {silver} AMD (per oz)  
"""

        bot.send_message(message.chat.id, text)

    else:
        bot.send_message(message.chat.id, "❌ Չհաջողվեց ստանալ տվյալները")


bot.polling()