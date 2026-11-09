from dataclasses import dataclass

from app.core.eventos import escuchar, publicar


@dataclass(frozen=True)
class _Algo:
    n: int


async def test_publicar_llama_a_los_manejadores_con_la_misma_conexion() -> None:
    llamadas: list[tuple[object, int]] = []

    @escuchar(_Algo)
    async def manejador(con: object, evento: _Algo) -> None:
        llamadas.append((con, evento.n))

    con = object()
    await publicar(con, _Algo(7))

    assert llamadas == [(con, 7)]


async def test_publicar_sin_manejadores_no_falla() -> None:
    @dataclass(frozen=True)
    class _SinOyentes:
        pass

    await publicar(object(), _SinOyentes())
