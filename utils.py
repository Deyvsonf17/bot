import os
import aiohttp

ID_ARQUIVO = "memes_enviados.txt"

def carregar_ids_enviados():
    """Carrega os IDs dos memes enviados de um arquivo."""
    if os.path.exists(ID_ARQUIVO):
        with open(ID_ARQUIVO, "r") as f:
            return set(f.read().splitlines())
    return set()

def salvar_id_meme(id_meme):
    """Salva um ID de meme no arquivo para evitar duplicatas."""
    with open(ID_ARQUIVO, "a") as f:
        f.write(id_meme + "\n")

async def is_image_url(url):
    """Verifica de forma assíncrona se uma URL é uma imagem."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as response:
                return 'image' in response.headers.get('Content-Type', '')
    except Exception:
        return False
