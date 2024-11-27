import asyncio
from telegram.ext import CommandHandler, CallbackQueryHandler, ApplicationBuilder
from commands import cm, add_meme, list_memes, stats, remove_meme, clear_fila, set_interval, fetch_new, toggle_envio_command
from tasks import enviar_memes
from handlers import callback_handler
from bot_config import TOKEN, bot
from state import bot_state  # Importa o estado global do bot

async def main():
    # Inicializa a aplicação do bot
    application = ApplicationBuilder().token(TOKEN).build()

    # Adicionar comandos
    application.add_handler(CommandHandler("cm", cm))
    application.add_handler(CommandHandler("add_meme", add_meme))
    application.add_handler(CommandHandler("list_memes", list_memes))
    application.add_handler(CommandHandler("remove_meme", remove_meme))
    application.add_handler(CommandHandler("clear_fila", clear_fila))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("set_interval", set_interval))
    application.add_handler(CommandHandler("fetch_new", fetch_new))
    application.add_handler(CommandHandler("toggle_envio", toggle_envio_command))

    # Adicionar callback handler
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Remove o webhook antes de iniciar o polling (evita conflito)
    print("🔧 Removendo webhook existente para evitar conflitos...")
    await bot.delete_webhook()

    # Tarefa principal de postagem
    async def loop_postagem():
        while True:
            if not await bot_state.is_envio_habilitado():  # Verifica o estado global
                print("🔴 Bot desligado. Loop de postagem pausado.")
                await asyncio.sleep(10)  # Evitar ocupação da CPU
                continue

            try:
                await enviar_memes()
                await asyncio.sleep(5)  # Intervalo de 5 segundos
            except Exception as e:
                print(f"Erro no loop de postagem: {e}")
                await asyncio.sleep(5)  # Evitar falhas permanentes

    # Inicia o loop de postagem
    loop_task = asyncio.create_task(loop_postagem())
    try:
        await application.run_polling()  # Inicia o polling para o bot
    finally:
        # Cancela o loop de postagem ao finalizar
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
