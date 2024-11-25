import asyncpraw
from telegram import Bot
import nest_asyncio

# Permitir loops múltiplos
nest_asyncio.apply()

# Configuração do Telegram Bot
TOKEN = "6333929876:AAHVBeNeA3w4a0mc0U5K1HZ3OlwDazMfecw"
CHAT_ID = "@testememe1"
ADMIN_ID = 530560530

# Inicializar o bot
bot = Bot(token=TOKEN)

# Configuração do Reddit API
reddit = asyncpraw.Reddit(
    client_id="SEb6fAeASTyFBthoIxqlRA",
    client_secret="LUiBsqhY97SmZJNBiO_RmrjmQ32g-w",
    user_agent="MemeBot v2.0"
)

# Lista de subreddits
subreddits = [
    "MemesBR", "MEMEBRASIL", "Memebras", "DiretoDoZapZap",
    "BRMemes", "MemesBrasil", "memesenapratica", "brasil", 
    "HUEstation", "AgiotasClub", "ShitpostBR", "porramauricio", "eu_nvr"
]

# Variável global de fila de memes
memes_fila = []

# Variável global para habilitar/desabilitar envio de mídia
envio_habilitado = True
