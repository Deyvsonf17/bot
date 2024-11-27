import random
from bot_config import CHAT_ID, bot, reddit, subreddits, ADMIN_ID
from utils import carregar_ids_enviados, salvar_id_meme, is_image_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import aiohttp
import asyncio
from state import bot_state  # Importa o estado global
from telegram.ext import CallbackContext






import random
from bot_config import bot, reddit, subreddits, ADMIN_ID
from utils import carregar_ids_enviados, salvar_id_meme, is_image_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import asyncio
from state import bot_state  # Importa o estado global

async def buscar_memes_reddit(ids_enviados):
    """Busca novos memes no Reddit."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando busca de memes no Reddit.")
        return []

    try:
        subreddit_nome = random.choice(subreddits)
        subreddit = await reddit.subreddit(subreddit_nome)
        posts = [post async for post in subreddit.hot(limit=50)]
    except Exception as e:
        print(f"Erro ao acessar subreddit: {e}")
        return []

    memes = [
        (post.url, post.title, post.id)
        for post in posts
        if post.id not in ids_enviados and await is_image_url(post.url)
    ]
    return memes[:5]  # Limitar a 20 memes

async def enviar_memes():
    """Envia memes para aprovação do administrador."""
    while True:
        if not await bot_state.is_envio_habilitado():  # Verificação antes de começar
            print("🔴 Bot está desligado. Ignorando envio de memes.")
            await asyncio.sleep(5)  # Esperar antes de verificar novamente
            continue

        ids_enviados = carregar_ids_enviados()
        memes = await buscar_memes_reddit(ids_enviados)

        if not memes:
            print("ℹ️ Nenhum novo meme encontrado para envio.")
            await asyncio.sleep(1800)  # Intervalo maior quando não há memes
            continue

        for url, title, post_id in memes:
            if not await bot_state.is_envio_habilitado():  # Verificação contínua dentro do loop
                print("🔴 Bot foi desligado. Abortando envio.")
                break

            try:
                print(f"Enviando meme {post_id} para aprovação.")
                keyboard = [
                    [
                        InlineKeyboardButton("Aprovar (com legenda)", callback_data=f"aprovar_com_legenda:{post_id}"),
                        InlineKeyboardButton("Aprovar (sem legenda)", callback_data=f"aprovar_sem_legenda:{post_id}")
                    ],
                    [InlineKeyboardButton("Reprovar", callback_data=f"reprovar:{post_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                async with aiohttp.ClientSession() as session:
                    await bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=url,
                        caption=f"{title}",  # Adiciona a legenda padrão para aprovação
                        reply_markup=reply_markup
                    )
                salvar_id_meme(post_id)
            except Exception as e:
                print(f"Erro ao enviar meme {post_id}: {e}")
            await asyncio.sleep(2)  # Intervalo entre envios
        await asyncio.sleep(30)  # Esperar antes de buscar novos memes

async def callback_handler(update: Update, context: CallbackContext):
    """Lida com os botões de aprovação/reprovação."""
    if not await bot_state.is_envio_habilitado():  # Verifica o estado antes de qualquer ação
        print("🔴 Bot está desligado. Ignorando interação com botões.")
        await update.callback_query.answer(
            "⚠️ O bot está desligado. Não é possível usar este botão agora.", show_alert=True
        )
        return

    query = update.callback_query
    await query.answer()

    action, post_id = query.data.split(":")
    message = query.message
    default_caption = "@centraldomeme"  # Legenda padrão

    # Obtendo o arquivo da foto
    try:
        photo_file_id = message.photo[-1].file_id
    except AttributeError:
        print("⚠️ A mensagem recebida não contém uma foto válida.")
        return

    # Apagar a mensagem original para evitar duplicidade
    try:
        await message.delete()
    except Exception as e:
        print(f"Erro ao apagar a mensagem original: {e}")

    # Processar a ação selecionada
    if action == "aprovar_com_legenda":
        try:
            # Adiciona @centraldomeme à legenda original
            original_caption = message.caption if message.caption else ""
            final_caption = f"{original_caption} | {default_caption}".strip()
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_file_id, caption=final_caption)
            print(f"✅ Enviado com legenda: {final_caption}")
        except Exception as e:
            print(f"Erro ao enviar imagem com legenda ao canal: {e}")
    elif action == "aprovar_sem_legenda":
        try:
            # Envia a foto com a legenda padrão
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_file_id, caption=default_caption)
            print(f"✅ Enviado sem legenda original, apenas com: {default_caption}")
        except Exception as e:
            print(f"Erro ao enviar imagem sem legenda ao canal: {e}")
    elif action == "reprovar":
        try:
            # Notifica a reprovação ao administrador
            await bot.send_message(chat_id=ADMIN_ID, text=f"❌ Meme ({post_id}) reprovado.")
            print(f"❌ Meme reprovado: {post_id}")
        except Exception as e:
            print(f"Erro ao enviar notificação de reprovação: {e}")
