"""Pasarela de IA: punto de entrada de la API.

Arrancar:  uvicorn app.main:app --reload
Documentación interactiva: http://localhost:8000/docs
"""
import time

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from app import proveedores, registro, router

app = FastAPI(title="Pasarela de IA", version="0.1.0")
con = registro.conectar()


class Mensaje(BaseModel):
    role: str
    content: str


class PeticionChat(BaseModel):
    model: str = "auto"          # "auto" = decide la pasarela
    messages: list[Mensaje]
    temperature: float | None = None
    max_tokens: int | None = None


@app.post("/v1/chat/completions")
async def chat(
    peticion: PeticionChat,
    x_usuario: str = Header("anonimo"),
    x_departamento: str = Header("general"),
):
    mensajes = [m.model_dump() for m in peticion.messages]
    texto = "\n".join(m["content"] for m in mensajes)
    decision = router.decidir(mensajes, x_departamento)

    opciones = {k: v for k, v in {"temperature": peticion.temperature,
                                  "max_tokens": peticion.max_tokens}.items() if v is not None}
    inicio = time.perf_counter()
    try:
        resultado = await proveedores.completar(decision.destino, decision.modelo, mensajes, **opciones)
        error = None
    except Exception as e:  # se registra también lo que falla
        resultado, error = None, str(e)[:300]
    ms = int((time.perf_counter() - inicio) * 1000)

    uso = (resultado or {}).get("usage", {})
    registro.guardar(
        con,
        usuario=x_usuario,
        departamento=x_departamento,
        decision=decision,
        texto=texto,
        tokens_entrada=uso.get("prompt_tokens", decision.tokens_estimados),
        tokens_salida=uso.get("completion_tokens", 0),
        milisegundos=ms,
        error=error,
    )

    if error:
        raise HTTPException(status_code=502, detail=f"Fallo del modelo {decision.modelo}: {error}")

    # Se añade la decisión a la respuesta para que sea transparente.
    resultado["pasarela"] = {"destino": decision.destino, "modelo": decision.modelo,
                             "motivo": decision.motivo}
    return resultado


@app.get("/resumen")
def ver_resumen():
    return registro.resumen(con)


@app.get("/salud")
def salud():
    return {"estado": "ok"}
