from telegram import Update
from telegram.ext import CallbackContext
from bot_config import bot, CHAT_ID
from state import bot_state  # Importa a instância global para controle do estado

async def callback_handler(update: Update, context: CallbackContext):
    """Lida com os botões de aprovação/reprovação."""
    if not await bot_state.is_envio_habilitado():  # Verifica o estado antes de qualquer ação
        print("🔴 Bot está desligado. Ignorando interação com botões.")
        await update.callback_query.answer(
            "⚠️ O bot está desligado. Não é possível usar este botão agora.", show_alert=True
        )
        return  # Ignorar completamente a interação

    query = update.callback_query
    await query.answer()

    action, post_id = query.data.split(":")
    message = query.message
    default_caption = "@centraldomeme"  # Legenda padrão

    try:
        # Recupera o ID do arquivo da foto
        photo_url = message.photo[-1].file_id
    except AttributeError:
        print("⚠️ A mensagem não contém uma foto válida.")
        return

    try:
        # Apaga a mensagem original para evitar duplicidade
        await message.delete()
    except Exception as e:
        print(f"Erro ao apagar a mensagem original: {e}")

    if action == "aprovar_com_legenda":
        try:
            # Combina a legenda original com a legenda padrão
            caption = message.caption.strip() if message.caption else ""

            # Configuração: Alterne entre "acima" ou "abaixo"
            # Para colocar o @centraldomeme em cima da legenda:
            final_caption = f"{default_caption}\n{caption}".strip()

            # Para colocar o @centraldomeme embaixo da legenda:
            # final_caption = f"{caption}\n{default_caption}".strip()

            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=final_caption)
            print(f"✅ Enviado com legenda: {final_caption}")
        except Exception as e:
            print(f"Erro ao enviar imagem com legenda ao canal: {e}")
    elif action == "aprovar_sem_legenda":
        try:
            # Envia a foto com apenas a legenda padrão
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=default_caption)
            print(f"✅ Enviado sem legenda original, apenas com: {default_caption}")
        except Exception as e:
            print(f"Erro ao enviar imagem sem legenda ao canal: {e}")
    elif action == "reprovar":
        try:
            # Notifica a reprovação ao administrador
            await bot.send_message(chat_id=CHAT_ID, text=f"❌ Meme ({post_id}) reprovado.")
            print(f"❌ Meme reprovado: {post_id}")
        except Exception as e:
            print(f"Erro ao enviar notificação de reprovação: {e}")
