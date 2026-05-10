"""
reservas.py — Clase Reserva con confirmación, cancelación, procesamiento
              y manejo exhaustivo de excepciones.
"""
import datetime
from entidades import Cliente
from servicios import Servicio
from excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoInconsistenteError,
    ParametroFaltanteError,
)
import logger


class EstadoReserva:
    PENDIENTE   = "Pendiente"
    CONFIRMADA  = "Confirmada"
    CANCELADA   = "Cancelada"
    PROCESADA   = "Procesada"
    ERROR       = "Error"


class Reserva:
    """
    Integra un Cliente con un Servicio, registra duración y gestiona estados.
    Implementa confirmación, cancelación y procesamiento con manejo de excepciones.
    """

    _contador: int = 0

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        fecha: datetime.date = None,
        descuento: float = 0.0,
        con_iva: bool = True,
    ):
        # ── Validaciones de entrada ────────────
        if cliente is None:
            raise ParametroFaltanteError("cliente")
        if servicio is None:
            raise ParametroFaltanteError("servicio")
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El parámetro 'cliente' no es instancia de Cliente")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El parámetro 'servicio' no es instancia de Servicio")
        if not cliente.activo:
            raise ReservaInvalidaError(f"Cliente '{cliente.nombre}' está inactivo")

        # ── Validar parámetros del servicio ───
        try:
            servicio.validar_parametros(duracion_horas)
        except Exception as exc:
            raise ReservaInvalidaError(str(exc)) from exc

        Reserva._contador += 1
        self._id            = Reserva._contador
        self._cliente       = cliente
        self._servicio      = servicio
        self._duracion      = duracion_horas
        self._fecha         = fecha or datetime.date.today()
        self._descuento     = descuento
        self._con_iva       = con_iva
        self._estado        = EstadoReserva.PENDIENTE
        self._costo_total   = None
        self._fecha_proceso = None

        logger.info(
            f"Reserva #{self._id} creada: cliente={cliente.nombre}, "
            f"servicio={servicio.nombre}, horas={duracion_horas}"
        )

    # ── Propiedades ────────────────────────────
    @property
    def id(self) -> int:
        return self._id

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def costo_total(self):
        return self._costo_total

    @property
    def duracion(self) -> float:
        return self._duracion

    # ── Operaciones de negocio ─────────────────
    def confirmar(self) -> str:
        """Confirma la reserva si está en estado Pendiente."""
        try:
            if self._estado != EstadoReserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    "confirmar",
                    f"solo se permite desde Pendiente; estado actual: {self._estado}"
                )
            self._estado = EstadoReserva.CONFIRMADA
            msg = f"Reserva #{self._id} confirmada para '{self._cliente.nombre}'"
            logger.info(msg)
            return msg
        except OperacionNoPermitidaError as exc:
            logger.error(f"Reserva #{self._id}: no se pudo confirmar", exc)
            raise

    def cancelar(self, motivo: str = "Sin motivo") -> str:
        """Cancela la reserva si no ha sido procesada."""
        try:
            if self._estado == EstadoReserva.PROCESADA:
                raise OperacionNoPermitidaError(
                    "cancelar", "no se puede cancelar una reserva ya procesada"
                )
            if self._estado == EstadoReserva.CANCELADA:
                raise OperacionNoPermitidaError("cancelar", "ya estaba cancelada")
            self._estado = EstadoReserva.CANCELADA
            msg = f"Reserva #{self._id} cancelada. Motivo: {motivo}"
            logger.advertencia(msg)
            return msg
        except OperacionNoPermitidaError as exc:
            logger.error(f"Reserva #{self._id}: cancelación rechazada", exc)
            raise

    def procesar(self) -> dict:
        """
        Procesa la reserva: calcula costo final y cambia estado a Procesada.
        Usa try/except/else/finally.
        """
        resultado = {}
        try:
            if self._estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
                raise OperacionNoPermitidaError(
                    "procesar",
                    f"estado actual no permite procesamiento: {self._estado}"
                )
            costo = self._servicio.calcular_costo_con(
                self._duracion,
                descuento=self._descuento,
                con_iva=self._con_iva,
            )
            if costo < 0:
                raise CalculoInconsistenteError("El costo calculado es negativo")

        except (OperacionNoPermitidaError, CalculoInconsistenteError) as exc:
            self._estado = EstadoReserva.ERROR
            logger.error(f"Reserva #{self._id}: error al procesar", exc)
            raise

        except Exception as exc:
            self._estado = EstadoReserva.ERROR
            logger.error(f"Reserva #{self._id}: error inesperado al procesar", exc)
            raise ReservaInvalidaError(f"Error inesperado: {exc}") from exc

        else:
            self._costo_total   = costo
            self._estado        = EstadoReserva.PROCESADA
            self._fecha_proceso = datetime.datetime.now()
            resultado = {
                "reserva_id"   : self._id,
                "cliente"      : self._cliente.nombre,
                "servicio"     : self._servicio.nombre,
                "duracion"     : self._duracion,
                "costo_total"  : self._costo_total,
                "estado"       : self._estado,
                "fecha_proceso": str(self._fecha_proceso),
            }
            logger.info(
                f"Reserva #{self._id} procesada. Costo=${self._costo_total:,.2f}"
            )

        finally:
            # Siempre registrar intento de procesamiento
            logger.info(
                f"Reserva #{self._id} — fin de procesamiento. Estado={self._estado}"
            )

        return resultado

    def describir(self) -> str:
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total else "pendiente"
        return (
            f"Reserva #{self._id}\n"
            f"  Cliente   : {self._cliente.nombre}\n"
            f"  Servicio  : {self._servicio.nombre} ({type(self._servicio).__name__})\n"
            f"  Duración  : {self._duracion} hora(s)\n"
            f"  Fecha     : {self._fecha}\n"
            f"  Descuento : {self._descuento*100:.0f}%\n"
            f"  IVA       : {'Sí' if self._con_iva else 'No'}\n"
            f"  Costo     : {costo_str}\n"
            f"  Estado    : {self._estado}"
        )

    def to_dict(self) -> dict:
        return {
            "id"          : self._id,
            "cliente"     : self._cliente.nombre,
            "servicio"    : self._servicio.nombre,
            "tipo_servicio": type(self._servicio).__name__,
            "duracion"    : self._duracion,
            "fecha"       : str(self._fecha),
            "descuento"   : self._descuento,
            "con_iva"     : self._con_iva,
            "costo_total" : self._costo_total,
            "estado"      : self._estado,
        }
