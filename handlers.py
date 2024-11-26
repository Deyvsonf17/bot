from telegram import Update
from telegram.ext import CallbackContext
from bot_config import bot, CHAT_ID, envio_habilitado

async def callback_handler(update: Update, context: CallbackContext):
    """Lida com os botões de aprovação/reprovação."""
    if not envio_habilitado:
        print("🔴 Envio de mensagens desabilitado.")
        return

    query = update.callback_query
    await query.answer()

    action, post_id = query.data.split(":")
    message = query.message
    caption = (
        message.caption.strip() if message.caption else None
    )
    photo_url = message.photo[-1].file_id  # Obtém o File ID da imagem

    try:
        # Apaga a mensagem original enviada ao administrador
        await message.delete()
    except Exception as e:
        print(f"Erro ao apagar a mensagem original: {e}")

    if action == "aprovar_com_legenda":
        # Envia a imagem com a legenda ao canal
        try:
            if caption:  # Envia com legenda se disponível
                await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=caption)
            else:  # Se não houver legenda, envia apenas a imagem
                await bot.send_photo(chat_id=CHAT_ID, photo=photo_url)
        except Exception as e:
            print(f"Erro ao enviar imagem com legenda ao canal: {e}")
    elif action == "aprovar_sem_legenda":
        # Envia a imagem sem legenda ao canal
        try:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url)
        except Exception as e:
            print(f"Erro ao enviar imagem sem legenda ao canal: {e}")
    elif action == "reprovar":
        # Notifica que o meme foi reprovado
        await query.message.reply_text(f"❌ Meme ({post_id}) reprovado. Nenhum envio ao canal foi feito.")
