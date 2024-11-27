import asyncio

class BotState:
    """Classe para centralizar o estado do bot."""
    def __init__(self):
        self._envio_habilitado = True  # Estado inicial
        self._lock = asyncio.Lock()

    async def toggle_envio(self):
        """Alterna o estado de envio entre habilitado e desabilitado."""
        async with self._lock:
            self._envio_habilitado = not self._envio_habilitado
            return self._envio_habilitado

    async def is_envio_habilitado(self):
        """Retorna o estado atual de envio."""
        async with self._lock:
            return self._envio_habilitado


# Instância global
bot_state = BotState()
