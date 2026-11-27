"""Detección básica de datos personales en español.

Fase 1: expresiones regulares. No es perfecto (en la fase 2 se puede
mejorar con un modelo), pero es rápido, explicable y no envía nada fuera.
"""
import re

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

_DNI = re.compile(r"\b(\d{8})[-\s]?([A-Za-z])\b")
_NIE = re.compile(r"\b([XYZxyz])[-\s]?(\d{7})[-\s]?([A-Za-z])\b")
_TELEFONO = re.compile(r"(?<!\d)(?:\+34[\s-]?)?[6789]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_IBAN = re.compile(r"\bES\d{2}(?:[\s-]?\d{4}){5}\b", re.IGNORECASE)


def _dni_valido(numero: str, letra: str) -> bool:
    return LETRAS_DNI[int(numero) % 23] == letra.upper()


def _nie_valido(prefijo: str, numero: str, letra: str) -> bool:
    equivalente = {"X": "0", "Y": "1", "Z": "2"}[prefijo.upper()]
    return LETRAS_DNI[int(equivalente + numero) % 23] == letra.upper()


def detectar(texto: str) -> list[str]:
    """Devuelve los tipos de dato personal encontrados (sin repetir)."""
    encontrados = []
    if any(_dni_valido(n, l) for n, l in _DNI.findall(texto)):
        encontrados.append("dni")
    if any(_nie_valido(p, n, l) for p, n, l in _NIE.findall(texto)):
        encontrados.append("nie")
    if _TELEFONO.search(texto):
        encontrados.append("telefono")
    if _EMAIL.search(texto):
        encontrados.append("email")
    if _IBAN.search(texto):
        encontrados.append("iban")
    return encontrados
