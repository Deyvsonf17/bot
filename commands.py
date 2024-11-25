from telegram import Update
from telegram.ext import CallbackContext
from utils import carregar_ids_enviados
from bot_config import ADMIN_ID, subreddits, envio_habilitado

# Variáveis globais
memes_fila = []
intervalo_postagens = 30  # Intervalo padrão de 30 minutos

async def cm(update: Update, context: CallbackContext):
    """Lista todos os comandos disponíveis com exemplos."""
    comandos = """
Comandos disponíveis:
/cm - Lista todos os comandos disponíveis.
/add_meme <URL> - Adiciona manualmente um meme à fila. Ex: /add_meme https://link-do-meme.com
/list_memes - Lista os memes na fila.
/remove_meme <índice> - Remove um meme da fila pelo índice. Ex: /remove_meme 1
/clear_fila - Limpa toda a fila de memes.
/stats - Exibe estatísticas do bot.
/set_interval <minutos> - Define o intervalo entre as postagens. Ex: /set_interval 10
/fetch_new - Busca novos memes do Reddit e adiciona à fila.
/toggle_envio - Habilita ou desabilita o envio de mídia para o canal.
"""
    await update.message.reply_text(comandos)

async def toggle_envio(update: Update, context: CallbackContext):
    """Habilita ou desabilita o envio de mídia para o canal."""
    global envio_habilitado
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        envio_habilitado = not envio_habilitado
        status = "habilitado" if envio_habilitado else "desabilitado"
        await update.message.reply_text(f"O envio de mídia foi {status}.")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")




async def add_meme(update: Update, context: CallbackContext):
    """Adiciona manualmente um meme à fila."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args:
            meme_url = context.args[0]
            if meme_url.startswith("http"):  # Valida se é uma URL
                memes_fila.append(meme_url)
                await update.message.reply_text(f"Meme adicionado à fila: {meme_url}")
            else:
                await update.message.reply_text("URL inválida. Exemplo: `/add_meme https://link-do-meme.com`")
        else:
            await update.message.reply_text("Envie o URL do meme após o comando. Exemplo: `/add_meme https://link-do-meme.com`")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def list_memes(update: Update, context: CallbackContext):
    """Lista os memes na fila de envio."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if memes_fila:
            lista_memes = "\n".join([f"{i+1}. {meme}" for i, meme in enumerate(memes_fila)])
            await update.message.reply_text(f"Memes na fila:\n{lista_memes}")
        else:
            await update.message.reply_text("A fila de memes está vazia.")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def remove_meme(update: Update, context: CallbackContext):
    """Remove um meme da fila pelo índice."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args and context.args[0].isdigit():
            indice = int(context.args[0]) - 1
            if 0 <= indice < len(memes_fila):
                meme_removido = memes_fila.pop(indice)
                await update.message.reply_text(f"Meme removido: {meme_removido}")
            else:
                await update.message.reply_text("Índice inválido.")
        else:
            await update.message.reply_text("Forneça o índice do meme a ser removido.")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def clear_fila(update: Update, context: CallbackContext):
    """Limpa toda a fila de memes."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        memes_fila.clear()
        await update.message.reply_text("Fila de memes limpa!")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def stats(update: Update, context: CallbackContext):
    """Exibe estatísticas do bot."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        post_count = len(carregar_ids_enviados())
        fila_count = len(memes_fila)
        await update.message.reply_text(f"Estatísticas do bot:\n- Memes postados: {post_count}\n- Memes na fila: {fila_count}")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def set_interval(update: Update, context: CallbackContext):
    """Altera o intervalo entre as postagens."""
    global intervalo_postagens
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args and context.args[0].isdigit():
            intervalo_postagens = int(context.args[0])
            await update.message.reply_text(f"Intervalo de postagens definido para {intervalo_postagens} minutos.")
        else:
            await update.message.reply_text("Comando inválido. Use: `/set_interval <minutos>`")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

async def fetch_new(update: Update, context: CallbackContext):
    """Busca novos memes do Reddit."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        from tasks import buscar_memes_reddit
        ids_enviados = carregar_ids_enviados()
        novos_memes = await buscar_memes_reddit(ids_enviados)
        if novos_memes:
            for url, title, post_id in novos_memes:
                memes_fila.append(url)
            await update.message.reply_text(f"{len(novos_memes)} novos memes adicionados à fila.")
        else:
            await update.message.reply_text("Nenhum novo meme encontrado no Reddit.")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
