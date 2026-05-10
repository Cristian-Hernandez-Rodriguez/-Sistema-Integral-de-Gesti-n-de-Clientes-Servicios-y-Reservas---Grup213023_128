"""
excepciones.py — Excepciones personalizadas del sistema Software FJ
"""


class SistemaFJError(Exception):
    """Excepción base del sistema."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERICO"):
        self.codigo = codigo
        super().__init__(mensaje)


class ClienteInvalidoError(SistemaFJError):
    def __init__(self, campo: str, valor):
        super().__init__(
            f"Dato inválido en campo '{campo}': {valor!r}",
            "ERR_CLIENTE"
        )
        self.campo = campo
        self.valor = valor


class ServicioNoDisponibleError(SistemaFJError):
    def __init__(self, servicio: str, razon: str = ""):
        msg = f"Servicio '{servicio}' no disponible"
        if razon:
            msg += f": {razon}"
        super().__init__(msg, "ERR_SERVICIO")


class ReservaInvalidaError(SistemaFJError):
    def __init__(self, detalle: str):
        super().__init__(f"Reserva inválida — {detalle}", "ERR_RESERVA")


class ParametroFaltanteError(SistemaFJError):
    def __init__(self, parametro: str):
        super().__init__(f"Parámetro obligatorio ausente: '{parametro}'", "ERR_PARAM")


class OperacionNoPermitidaError(SistemaFJError):
    def __init__(self, operacion: str, razon: str = ""):
        msg = f"Operación no permitida: '{operacion}'"
        if razon:
            msg += f" — {razon}"
        super().__init__(msg, "ERR_OPERACION")


class CalculoInconsistenteError(SistemaFJError):
    def __init__(self, detalle: str):
        super().__init__(f"Cálculo inconsistente: {detalle}", "ERR_CALCULO")
