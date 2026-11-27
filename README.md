# Pasarela de IA para la administración pública

Una puerta de entrada única para que una organización use IA **sin sacar datos personales fuera, sin gastar de más y sabiendo en todo momento qué se hace**.

## El problema

Hablando con empresas que implantan IA en ayuntamientos (InproInnova, Sevilla, noviembre de 2026) aparecieron tres problemas:

1. **Soberanía de datos:** la administración no quiere que sus datos acaben en servidores de empresas extranjeras.
2. **Coste:** usar el modelo más caro para todo es matar moscas a cañonazos.
3. **Trazabilidad:** hay que poder explicar quién usó la IA, para qué y con qué modelo.

## Qué hace (fase 1)

- Recibe peticiones con el mismo formato que la API de OpenAI, así que cualquier aplicación puede usarla sin cambios.
- Detecta datos personales (DNI, NIE, teléfono, email, IBAN). Si los hay, la petición va **siempre al modelo local**.
- Algunos departamentos (padrón, servicios sociales…) solo pueden usar el modelo local.
- Las tareas largas o complejas van a un modelo de pago y las sencillas, al local.
- Registra cada petición con su **motivo**, sus tokens y su coste. **No guarda el texto**, solo una huella, para que el registro no se convierta en otro almacén de datos personales.

## Cómo probarlo

```bash
# 1. Modelo local
ollama pull llama3.2:3b

# 2. Entorno
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # y rellena tu clave
set -a && source .env && set +a   # carga las variables (en Windows, defínelas a mano)

# 3. Tests
pytest

# 4. Arrancar
uvicorn app.main:app --reload
# Documentación interactiva: http://localhost:8000/docs

# 5. Peticiones de ejemplo
python scripts/probar.py
```

## Decisiones de diseño

| Decisión | Por qué |
| --- | --- |
| Reglas en lugar de IA para enrutar | Son explicables y auditables: cada decisión tiene un motivo legible |
| Los datos personales mandan sobre todo lo demás | Proteger los datos es más importante que la calidad o el coste |
| No guardar el texto de las peticiones | El registro de auditoría no debe convertirse en un riesgo |
| API compatible con OpenAI | Se integra con herramientas existentes sin cambiarlas |

## Próximas fases

- **Fase 2:** clasificar la dificultad con un modelo pequeño, mejorar la detección de datos personales y un panel de gasto por departamento.
- **Fase 3:** informes de auditoría exportables y documentación del sistema orientada a la ley europea de IA.
