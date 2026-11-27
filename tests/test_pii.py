from app.pii import detectar


def test_dni_valido_se_detecta():
    assert "dni" in detectar("El solicitante con DNI 12345678Z pide cita")


def test_dni_con_letra_incorrecta_no_se_detecta():
    assert "dni" not in detectar("Referencia 12345678A del expediente")


def test_nie_valido():
    assert "nie" in detectar("NIE X1234567L")


def test_telefono_email_iban():
    texto = "Llamar al 612 345 678, escribir a ana@ayto.es, IBAN ES91 2100 0418 4502 0005 1332"
    assert set(detectar(texto)) >= {"telefono", "email", "iban"}


def test_texto_sin_datos_personales():
    assert detectar("¿Qué horario tiene la biblioteca municipal?") == []
