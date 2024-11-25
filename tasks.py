import random
from bot_config import bot, reddit, ADMIN_ID, subreddits, envio_habilitado
from utils import carregar_ids_enviados, salvar_id_meme, is_image_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import asyncio

async def buscar_memes_reddit(ids_enviados):
    """Busca novos memes no Reddit."""
    try:
        subreddit_nome = random.choice(subreddits)
        print(f"Buscando memes no subreddit: {subreddit_nome}")
        subreddit = await reddit.subreddit(subreddit_nome)

        posts = [post async for post in subreddit.hot(limit=50)]
    except Exception as e:
        print(f"Erro ao acessar subreddit {subreddit_nome}: {e}")
        return []

    memes = [
        (post.url, post.title, post.id)
        for post in posts
        if post.id not in ids_enviados and await is_image_url(post.url)
    ]
    print(f"Memes encontrados: {len(memes)}")
    return memes[:5]  # Limitar a 5 memes

async def enviar_memes():
    """Envia memes para aprovação do administrador."""
    global envio_habilitado

    if not envio_habilitado:
        print("🔴 Envio de mídia está desativado. Aguardando...")
        return

    ids_enviados = carregar_ids_enviados()

    # Busca novos memes
    memes = await buscar_memes_reddit(ids_enviados)
    if not memes:
        print("Nenhum novo meme encontrado para envio.")
        return

    for url, title, post_id in memes:
        if not envio_habilitado:
            print("Envio de mídia foi desativado durante a execução. Abortando.")
            break

        try:
            print(f"Preparando envio do meme {post_id}...")
            keyboard = [
                [
                    InlineKeyboardButton("Aprovar (com legenda)", callback_data=f"aprovar_com_legenda:{post_id}"),
                    InlineKeyboardButton("Aprovar (sem legenda)", callback_data=f"aprovar_sem_legenda:{post_id}")
                ],
                [InlineKeyboardButton("Reprovar", callback_data=f"reprovar:{post_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            async with aiohttp.ClientSession() as session:  # Garante fechamento da sessão
                await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=url,
                    caption=f"{title}",
                    reply_markup=reply_markup
                )
            salvar_id_meme(post_id)
            print(f"Meme {post_id} enviado para aprovação.")
        except Exception as e:
            print(f"Erro ao enviar meme {post_id} para aprovação: {e}")
        await asyncio.sleep(2)  # Intervalo entre envios
