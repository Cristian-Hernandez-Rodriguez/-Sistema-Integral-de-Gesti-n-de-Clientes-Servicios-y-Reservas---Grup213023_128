"""
gestor.py — Gestor central de Software FJ (sin base de datos).
             Administra listas de clientes, servicios y reservas.
"""
from entidades import Cliente
from servicios import Servicio
from reservas import Reserva
from excepciones import SistemaFJError, ReservaInvalidaError
import logger


class GestorSistema:
    """Administra todas las entidades del sistema en memoria."""

    def __init__(self):
        self._clientes:  list[Cliente]  = []
        self._servicios: list[Servicio] = []
        self._reservas:  list[Reserva]  = []
        logger.info("GestorSistema inicializado")

    # ── Clientes ───────────────────────────────
    def registrar_cliente(self, **kwargs) -> Cliente:
        try:
            c = Cliente(**kwargs)
            self._clientes.append(c)
            return c
        except SistemaFJError as exc:
            logger.error("Error registrando cliente", exc)
            raise

    def buscar_cliente(self, documento: str) -> Cliente | None:
        for c in self._clientes:
            if c.documento == documento:
                return c
        return None

    def listar_clientes(self) -> list[dict]:
        return [c.to_dict() for c in self._clientes]

    # ── Servicios ──────────────────────────────
    def agregar_servicio(self, servicio: Servicio) -> Servicio:
        try:
            if not servicio.validar():
                raise ReservaInvalidaError(f"Servicio '{servicio.nombre}' no pasó validación")
            self._servicios.append(servicio)
            logger.info(f"Servicio agregado al gestor: {servicio.nombre}")
            return servicio
        except SistemaFJError as exc:
            logger.error("Error agregando servicio", exc)
            raise

    def listar_servicios(self) -> list[dict]:
        return [s.to_dict() for s in self._servicios]

    # ── Reservas ───────────────────────────────
    def crear_reserva(self, cliente: Cliente, servicio: Servicio,
                      duracion_horas: float, **kwargs) -> Reserva:
        try:
            r = Reserva(cliente, servicio, duracion_horas, **kwargs)
            self._reservas.append(r)
            return r
        except SistemaFJError as exc:
            logger.error("Error creando reserva", exc)
            raise

    def listar_reservas(self) -> list[dict]:
        return [r.to_dict() for r in self._reservas]

    def obtener_reserva(self, reserva_id: int) -> Reserva | None:
        for r in self._reservas:
            if r.id == reserva_id:
                return r
        return None

    # ── Estadísticas ───────────────────────────
    def resumen(self) -> dict:
        procesadas = [r for r in self._reservas if r.estado == "Procesada"]
        ingresos   = sum(r.costo_total for r in procesadas if r.costo_total)
        return {
            "total_clientes" : len(self._clientes),
            "total_servicios": len(self._servicios),
            "total_reservas" : len(self._reservas),
            "reservas_procesadas": len(procesadas),
            "ingresos_totales": ingresos,
        }
