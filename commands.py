from telegram import Update
from telegram.ext import CallbackContext
from bot_config import ADMIN_ID
from state import bot_state  # Importa a instância global

# Variáveis globais
intervalo_postagens = 30  # Intervalo padrão de 30 minutos
memes_fila = []  # Fila de memes


async def cm(update: Update, context: CallbackContext):
    """Lista todos os comandos disponíveis com exemplos."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /cm.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

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
/toggle_envio - Habilita ou desabilita todo tipo de envio do bot.
"""
    print("ℹ️ DEBUG: Comando /cm executado com sucesso.")
    await update.message.reply_text(comandos)


async def toggle_envio_command(update: Update, context: CallbackContext):
    """Habilita ou desabilita o envio de mídia e mensagens pelo bot."""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        novo_estado = await bot_state.toggle_envio()  # Alterna o estado
        status = "habilitado" if novo_estado else "desabilitado"
        print(f"🔧 DEBUG: Bot foi {'ligado' if novo_estado else 'desligado'}.")
        await update.message.reply_text(f"Envio de mídia e mensagens foi {status}.")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /toggle_envio.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def fetch_new(update: Update, context: CallbackContext):
    """Busca novos memes do Reddit."""
    from tasks import buscar_memes_reddit
    from utils import carregar_ids_enviados

    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /fetch_new.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode buscar novos memes.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        print("ℹ️ DEBUG: Comando /fetch_new recebido.")
        ids_enviados = carregar_ids_enviados()
        novos_memes = await buscar_memes_reddit(ids_enviados)
        if novos_memes:
            for url, title, post_id in novos_memes:
                memes_fila.append(url)
            print(f"ℹ️ DEBUG: {len(novos_memes)} novos memes adicionados à fila.")
            await update.message.reply_text(f"{len(novos_memes)} novos memes adicionados à fila.")
        else:
            print("ℹ️ DEBUG: Nenhum novo meme encontrado no Reddit.")
            await update.message.reply_text("Nenhum novo meme encontrado no Reddit.")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /fetch_new.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def add_meme(update: Update, context: CallbackContext):
    """Adiciona manualmente um meme à fila."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /add_meme.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args:
            meme_url = context.args[0]
            if meme_url.startswith("http"):
                memes_fila.append(meme_url)
                print(f"ℹ️ DEBUG: Meme adicionado à fila: {meme_url}")
                await update.message.reply_text(f"Meme adicionado à fila: {meme_url}")
            else:
                print("⚠️ DEBUG: URL inválida fornecida para /add_meme.")
                await update.message.reply_text("URL inválida. Exemplo: `/add_meme https://link-do-meme.com`")
        else:
            print("⚠️ DEBUG: Nenhum URL fornecido para /add_meme.")
            await update.message.reply_text("Envie o URL do meme após o comando. Exemplo: `/add_meme https://link-do-meme.com`")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /add_meme.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def list_memes(update: Update, context: CallbackContext):
    """Lista os memes na fila."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /list_memes.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if memes_fila:
            lista_memes = "\n".join([f"{i+1}. {meme}" for i, meme in enumerate(memes_fila)])
            print(f"ℹ️ DEBUG: Memes listados com sucesso. Total: {len(memes_fila)}")
            await update.message.reply_text(f"Memes na fila:\n{lista_memes}")
        else:
            print("ℹ️ DEBUG: A fila de memes está vazia.")
            await update.message.reply_text("A fila de memes está vazia.")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /list_memes.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def remove_meme(update: Update, context: CallbackContext):
    """Remove um meme da fila pelo índice."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /remove_meme.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args and context.args[0].isdigit():
            indice = int(context.args[0]) - 1
            if 0 <= indice < len(memes_fila):
                meme_removido = memes_fila.pop(indice)
                print(f"ℹ️ DEBUG: Meme removido: {meme_removido}")
                await update.message.reply_text(f"Meme removido: {meme_removido}")
            else:
                print(f"⚠️ DEBUG: Índice inválido fornecido para /remove_meme: {indice}")
                await update.message.reply_text("Índice inválido.")
        else:
            print("⚠️ DEBUG: Índice não fornecido ou inválido para /remove_meme.")
            await update.message.reply_text("Forneça o índice do meme a ser removido.")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /remove_meme.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def clear_fila(update: Update, context: CallbackContext):
    """Limpa toda a fila de memes."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /clear_fila.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        memes_fila.clear()
        print("ℹ️ DEBUG: Fila de memes limpa com sucesso.")
        await update.message.reply_text("Fila de memes limpa!")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /clear_fila.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def stats(update: Update, context: CallbackContext):
    """Exibe estatísticas do bot."""
    from utils import carregar_ids_enviados

    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /stats.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        post_count = len(carregar_ids_enviados())
        fila_count = len(memes_fila)
        print(f"ℹ️ DEBUG: Estatísticas consultadas - Postados: {post_count}, Na fila: {fila_count}")
        await update.message.reply_text(f"Estatísticas do bot:\n- Memes postados: {post_count}\n- Memes na fila: {fila_count}")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /stats.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")


async def set_interval(update: Update, context: CallbackContext):
    """Altera o intervalo entre as postagens."""
    if not await bot_state.is_envio_habilitado():
        print("🔴 Bot está desligado. Ignorando comando /set_interval.")
        await update.message.reply_text("⚠️ O bot está desligado e não pode processar comandos.")
        return

    global intervalo_postagens
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if context.args and context.args[0].isdigit():
            intervalo_postagens = int(context.args[0])
            print(f"ℹ️ DEBUG: Intervalo de postagens alterado para {intervalo_postagens} minutos.")
            await update.message.reply_text(f"Intervalo de postagens definido para {intervalo_postagens} minutos.")
        else:
            print("⚠️ DEBUG: Argumento inválido para /set_interval.")
            await update.message.reply_text("Comando inválido. Use: `/set_interval <minutos>`")
    else:
        print(f"⚠️ DEBUG: Usuário não autorizado ({user_id}) tentou usar /set_interval.")
        await update.message.reply_text("Você não tem permissão para usar este comando.")
