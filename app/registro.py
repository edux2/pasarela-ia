"""Registro de cada petición en SQLite (trazabilidad y costes).

Decisión de gobernanza: NO se guarda el texto de la petición, solo una
huella (hash) y su longitud. Si guardáramos el texto, el propio registro
se convertiría en un almacén de datos personales.
"""
import hashlib
import sqlite3
from datetime import datetime, timezone

from app import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS peticiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    usuario TEXT NOT NULL,
    departamento TEXT NOT NULL,
    destino TEXT NOT NULL,
    modelo TEXT NOT NULL,
    motivo TEXT NOT NULL,
    datos_personales TEXT NOT NULL,
    huella_peticion TEXT NOT NULL,
    caracteres INTEGER NOT NULL,
    tokens_entrada INTEGER NOT NULL,
    tokens_salida INTEGER NOT NULL,
    coste_eur REAL NOT NULL,
    milisegundos INTEGER NOT NULL,
    error TEXT
)
"""


def conectar(ruta: str | None = None) -> sqlite3.Connection:
    con = sqlite3.connect(ruta or config.RUTA_BD)
    con.row_factory = sqlite3.Row
    con.execute(ESQUEMA)
    return con


def calcular_coste(modelo: str, tokens_entrada: int, tokens_salida: int) -> float:
    precio = config.PRECIOS.get(modelo, {"entrada": 0.0, "salida": 0.0})
    return (tokens_entrada * precio["entrada"] + tokens_salida * precio["salida"]) / 1_000_000


def guardar(con, *, usuario, departamento, decision, texto, tokens_entrada,
            tokens_salida, milisegundos, error=None) -> None:
    con.execute(
        """INSERT INTO peticiones (fecha, usuario, departamento, destino, modelo,
           motivo, datos_personales, huella_peticion, caracteres, tokens_entrada,
           tokens_salida, coste_eur, milisegundos, error)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            usuario,
            departamento,
            decision.destino,
            decision.modelo,
            decision.motivo,
            ",".join(decision.datos_personales),
            hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16],
            len(texto),
            tokens_entrada,
            tokens_salida,
            calcular_coste(decision.modelo, tokens_entrada, tokens_salida),
            milisegundos,
            error,
        ),
    )
    con.commit()


def resumen(con) -> dict:
    """Gasto y uso agrupados por departamento y por modelo."""
    def agrupar(columna):
        filas = con.execute(
            f"""SELECT {columna} AS clave, COUNT(*) AS peticiones,
                       SUM(tokens_entrada + tokens_salida) AS tokens,
                       ROUND(SUM(coste_eur), 4) AS coste_eur
                FROM peticiones GROUP BY {columna} ORDER BY coste_eur DESC"""
        ).fetchall()
        return [dict(f) for f in filas]

    total = con.execute(
        "SELECT COUNT(*) AS peticiones, ROUND(COALESCE(SUM(coste_eur), 0), 4) AS coste_eur, "
        "SUM(CASE WHEN destino = 'local' THEN 1 ELSE 0 END) AS al_local FROM peticiones"
    ).fetchone()
    return {
        "total": dict(total),
        "por_departamento": agrupar("departamento"),
        "por_modelo": agrupar("modelo"),
    }
