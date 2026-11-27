"""Envía unas peticiones de ejemplo a la pasarela y muestra a dónde fue cada una.

Uso (con la pasarela arrancada):  python scripts/probar.py
"""
import requests

URL = "http://localhost:8000"

EJEMPLOS = [
    ("atencion_ciudadana", "¿A qué hora abre el registro municipal?"),
    ("padron", "Necesito el certificado de empadronamiento de mi madre"),
    ("urbanismo", "El vecino con DNI 12345678Z solicita licencia de obra menor"),
    ("urbanismo", "Compara la ordenanza de terrazas de 2019 con la de 2024 y dime qué cambia"),
]

for departamento, texto in EJEMPLOS:
    r = requests.post(
        f"{URL}/v1/chat/completions",
        json={"model": "auto", "messages": [{"role": "user", "content": texto}]},
        headers={"x-usuario": "prueba", "x-departamento": departamento},
        timeout=180,
    )
    if r.ok:
        p = r.json()["pasarela"]
        print(f"[{departamento}] {texto[:50]}...\n   -> {p['destino']} ({p['modelo']}): {p['motivo']}\n")
    else:
        print(f"[{departamento}] ERROR {r.status_code}: {r.text[:200]}\n")

print("Resumen:", requests.get(f"{URL}/resumen", timeout=10).json())
