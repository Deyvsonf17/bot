import asyncio
from telegram.ext import CommandHandler, CallbackQueryHandler, ApplicationBuilder
from commands import cm, add_meme, list_memes, stats, remove_meme, clear_fila, set_interval, fetch_new, toggle_envio
from tasks import enviar_memes
from handlers import callback_handler
from bot_config import TOKEN

async def main():
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
    application.add_handler(CommandHandler("toggle_envio", toggle_envio))

    # Adicionar callback handler
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Tarefa principal de postagem
    async def loop_postagem():
        while True:
            try:
                await enviar_memes()
                await asyncio.sleep(1600)  # Intervalo de meia hora
            except Exception as e:
                print(f"Erro no loop de postagem: {e}")
                await asyncio.sleep(10)  # Evitar falhas permanentes

    loop_task = asyncio.create_task(loop_postagem())
    try:
        await application.run_polling()
    finally:
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
