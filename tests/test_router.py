from app import config
from app.router import decidir


def msg(texto):
    return [{"role": "user", "content": texto}]


def test_datos_personales_van_a_local():
    d = decidir(msg("Analiza el expediente de DNI 12345678Z"), "urbanismo")
    assert d.destino == "local" and "dni" in d.motivo


def test_departamento_solo_local():
    d = decidir(msg("Compara estas dos convocatorias"), "padron")
    assert d.destino == "local"


def test_tarea_compleja_va_a_pago():
    d = decidir(msg("Compara estas dos ordenanzas de terrazas"), "urbanismo")
    assert d.destino == "pago" and d.modelo == config.PAGO_MODEL


def test_texto_largo_va_a_pago():
    d = decidir(msg("palabra " * 2000), "urbanismo")
    assert d.destino == "pago"


def test_tarea_sencilla_va_a_local():
    d = decidir(msg("¿A qué hora abre el registro?"), "atencion_ciudadana")
    assert d.destino == "local" and d.motivo == "tarea sencilla"
