"""Enrutador de reglas: decide a qué modelo va cada petición y por qué.

Cada decisión lleva un motivo legible: es la base de la trazabilidad.
"""
from dataclasses import dataclass, field

from app import config, pii


@dataclass
class Decision:
    destino: str          # "local" o "pago"
    modelo: str
    motivo: str           # explicación legible de por qué se eligió
    datos_personales: list[str] = field(default_factory=list)
    tokens_estimados: int = 0


def estimar_tokens(texto: str) -> int:
    """Aproximación: en español, unos 4 caracteres por token."""
    return max(1, len(texto) // 4)


def decidir(mensajes: list[dict], departamento: str) -> Decision:
    texto = "\n".join(str(m.get("content", "")) for m in mensajes)
    tokens = estimar_tokens(texto)
    personales = pii.detectar(texto)

    def local(motivo):
        return Decision("local", config.LOCAL_MODEL, motivo, personales, tokens)

    def pago(motivo):
        return Decision("pago", config.PAGO_MODEL, motivo, personales, tokens)

    # 1. Los datos personales nunca salen del servidor.
    if personales:
        return local(f"datos personales detectados: {', '.join(personales)}")

    # 2. Algunos departamentos solo pueden usar el modelo local.
    if departamento in config.DEPARTAMENTOS_SOLO_LOCAL:
        return local(f"el departamento '{departamento}' solo usa modelo local")

    # 3. Las tareas largas o complejas van al modelo de pago.
    if tokens > config.UMBRAL_TOKENS_COMPLEJO:
        return pago(f"texto largo ({tokens} tokens estimados)")
    texto_min = texto.lower()
    for palabra in config.PALABRAS_COMPLEJAS:
        if palabra in texto_min:
            return pago(f"tarea compleja (contiene '{palabra}')")

    # 4. Por defecto, lo más barato que sirve.
    return local("tarea sencilla")
