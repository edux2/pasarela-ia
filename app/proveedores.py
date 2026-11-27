"""Llamada a los modelos.

Ollama y la mayoría de proveedores de pago aceptan el mismo formato
(el de OpenAI), así que basta con un único cliente.
"""
import httpx

from app import config


async def completar(destino: str, modelo: str, mensajes: list[dict], **opciones) -> dict:
    if destino == "local":
        base_url, clave = config.LOCAL_BASE_URL, "ollama"
    else:
        base_url, clave = config.PAGO_BASE_URL, config.PAGO_API_KEY

    cuerpo = {"model": modelo, "messages": mensajes, **opciones}
    async with httpx.AsyncClient(timeout=120) as cliente:
        respuesta = await cliente.post(
            f"{base_url}/chat/completions",
            json=cuerpo,
            headers={"Authorization": f"Bearer {clave}"},
        )
        respuesta.raise_for_status()
        return respuesta.json()
