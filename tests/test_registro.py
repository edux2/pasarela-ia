from app import config, registro
from app.router import decidir


def test_guardar_y_resumir(monkeypatch):
    monkeypatch.setitem(config.PRECIOS, config.PAGO_MODEL, {"entrada": 1.0, "salida": 3.0})
    con = registro.conectar(":memory:")

    d_pago = decidir([{"role": "user", "content": "Compara estos dos contratos"}], "urbanismo")
    registro.guardar(con, usuario="ana", departamento="urbanismo", decision=d_pago,
                     texto="Compara estos dos contratos", tokens_entrada=1_000_000,
                     tokens_salida=1_000_000, milisegundos=900)

    d_local = decidir([{"role": "user", "content": "Mi DNI es 12345678Z"}], "padron")
    registro.guardar(con, usuario="luis", departamento="padron", decision=d_local,
                     texto="Mi DNI es 12345678Z", tokens_entrada=50,
                     tokens_salida=20, milisegundos=300)

    r = registro.resumen(con)
    assert r["total"]["peticiones"] == 2
    assert r["total"]["al_local"] == 1
    assert r["total"]["coste_eur"] == 4.0
    assert r["por_departamento"][0]["clave"] == "urbanismo"


def test_no_se_guarda_el_texto():
    con = registro.conectar(":memory:")
    d = decidir([{"role": "user", "content": "Mi DNI es 12345678Z"}], "padron")
    registro.guardar(con, usuario="luis", departamento="padron", decision=d,
                     texto="Mi DNI es 12345678Z", tokens_entrada=10, tokens_salida=5,
                     milisegundos=10)
    fila = dict(con.execute("SELECT * FROM peticiones").fetchone())
    assert "12345678Z" not in " ".join(str(v) for v in fila.values())
