from telegram import Update
from telegram.ext import CallbackContext
from bot_config import bot, CHAT_ID


async def callback_handler(update: Update, context: CallbackContext):
    """Lida com os botões de aprovação/reprovação."""
    query = update.callback_query
    await query.answer()

    # Extrai a ação e o ID do post
    action, post_id = query.data.split(":")
    message = query.message
    caption = message.caption.split("Legenda proposta:", 1)[1].strip() if "Legenda proposta:" in message.caption else ""
    photo_url = message.photo[-1].file_id  # File ID da imagem enviada ao admin

    try:
        # Apaga a mensagem original enviada ao administrador (imagem e botões)
        await message.delete()
    except Exception as e:
        print(f"Erro ao apagar a mensagem original: {e}")

    # Realiza a ação com base no botão clicado
    if action == "aprovar_com_legenda":
        # Envia a imagem com a legenda original ao canal
        try:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=caption)
        except Exception as e:
            print(f"Erro ao enviar imagem com legenda ao canal: {e}")
        # Notifica o administrador
        await query.message.reply_text(f"✅ Meme ({post_id}) aprovado com legenda original e enviado ao canal.")
    elif action == "aprovar_sem_legenda":
        # Envia a imagem sem legenda ao canal
        try:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url)
        except Exception as e:
            print(f"Erro ao enviar imagem sem legenda ao canal: {e}")
        # Notifica o administrador
        await query.message.reply_text(f"✅⚠ Meme ({post_id}) aprovado sem legenda e enviado ao canal.")
    elif action == "reprovar":
        # Notifica que o meme foi reprovado
        await query.message.reply_text(f"❌ Meme ({post_id}) reprovado. Nenhum envio ao canal foi feito.")
